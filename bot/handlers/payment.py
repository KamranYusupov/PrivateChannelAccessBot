import json
from json import JSONDecodeError

import loguru
from aiogram import Router, types, F
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder
import pydantic
from django.conf import settings

from bot.keyboards.inline import get_inline_keyboard
from common.exceptions import PaymentAlreadyProcessed
from services.infra.product_callback import (
    ProductCallbackService,
)
from services.infra.ykassa_payload import YKASSAPayloadService
from services.business.payment import PaymentUseCase
from web.apps.payments.models import MerchantType, Payment
from web.apps.telegram_users.models import TelegramUser
from web.db.orm_utils import aget_or_none
from web.apps.subscriptions.tasks.business.invite_link import (
    create_and_send_invite_link_task,
)

router = Router()

@router.callback_query(F.data.startswith('buy_'))
async def buy_product_tariff(
    callback: types.CallbackQuery,
):
    merchant_type_buttons = {
        merchant_type.label: f'{merchant_type.value}_{callback.data}'
        for merchant_type in MerchantType
    }
    sizes = (1, ) * len(merchant_type_buttons)

    await callback.message.edit_text(
        'Выберите способ оплаты:',
        reply_markup=get_inline_keyboard(
            buttons=merchant_type_buttons,
            sizes=sizes,
        )
    )
    return

@router.callback_query(
    F.data.startswith(f'{MerchantType.YKASSA.value}_buy')
)
async def send_ykassa_invoice(
    callback: types.CallbackQuery,
):
    callback_data = callback.data.split('_')
    product_type_value, tariff_id = callback_data[-2:]

    tariff_model = ProductCallbackService.get_tariff_model_by_product_type_value(
        product_type_value
    )
    product_type = ProductCallbackService.get_product_type_by_value(
        product_type_value
    )
    if not tariff_model or not product_type:
        await callback.message.delete()
        return

    tariff = await aget_or_none(tariff_model.objects.all(), id=tariff_id)
    await callback.message.delete()

    if not tariff:
        loguru.logger.info(f'Tariff {tariff_id} not found.')
        return

    amount = int(tariff.price) * 100
    invoice_payload = {
        'product_type_value': product_type_value,
        'tariff_id': tariff_id,
    }

    payment = await Payment.objects.acreate(
        amount=tariff.price,
        product_type=product_type,
        merchant_type=MerchantType.YKASSA,
        merchant_payload=invoice_payload,
    )
    invoice_payload['payment_id'] = payment.id
    await callback.message.answer_invoice(
        title=tariff.title,
        description=tariff.description,
        payload=json.dumps(invoice_payload),
        provider_token=settings.YKASSA_TOKEN,
        currency='RUB',
        test=True,
        prices=[LabeledPrice(label=tariff.title, amount=amount)],
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(
        pre_checkout_query: types.PreCheckoutQuery,
):
    try:
        invoice_payload_schema = YKASSAPayloadService.get_invoice_payload_schema(
            pre_checkout_query.invoice_payload,
        )
    except (pydantic.ValidationError, JSONDecodeError):
        await pre_checkout_query.bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=False,
            error_message='Ошибка данных. Попробуйте еще раз.',
        )
        return

    tariff_model = ProductCallbackService.get_tariff_model_by_product_type_value(
        invoice_payload_schema.product_type_value
    )
    tariff = await aget_or_none(
        tariff_model.objects.all(),
        id=invoice_payload_schema.tariff_id
    )
    if not tariff:
        await pre_checkout_query.answer(
            ok=False,
            error_message='Тариф был удален. Попробуйте оплатить другой.'
        )
        return

    expected_amount = int(tariff.price * 100)
    if pre_checkout_query.total_amount != expected_amount:
        await pre_checkout_query.answer(
            ok=False,
            error_message='Цена тарифа изменилась. Попробуйте выбрать снова.'
        )
        return

    await pre_checkout_query.answer(
        ok=True,
    )


@router.message(F.successful_payment)
async def successful_payment(
        message: types.Message,
):
    data_error_msg = (
        'Произошла ошибка данных. '
        f'Обратитесь в поддержку {settings.SUPPORT_USERNAME}.'
    )
    try:
        invoice_payload_schema = YKASSAPayloadService.get_invoice_payload_schema(
            message.successful_payment.invoice_payload,
        )
    except (pydantic.ValidationError, JSONDecodeError):
        await message.answer(data_error_msg)
        return

    product_type = ProductCallbackService.get_product_type_by_value(
        invoice_payload_schema.product_type_value
    )

    if product_type != product_type.PRIVATE_CHANNEL_ACCESS:
        await message.answer(
            text=(
                'Функционал пока не поддерживается. '
                f'Обратитесь в поддержку {settings.SUPPORT_USERNAME}.'
            ),
        )
        return

    telegram_user_id = await TelegramUser.objects.get_id_by_telegram_id(
        telegram_id=message.from_user.id,
    )
    loguru.logger.info(str(telegram_user_id))
    try:
        subscription = await PaymentUseCase.process_subscription_payment(
            telegram_user_id=telegram_user_id,
            payment_id=invoice_payload_schema.payment_id,
            tariff_id=invoice_payload_schema.tariff_id,
        )
    except Payment.DoesNotExist:
        await message.answer(data_error_msg)
        return
    except PaymentAlreadyProcessed:
        return

    try:
        limited_link_obj = await message.bot.create_chat_invite_link(
            chat_id=settings.PRIVATE_CHANNEL_ID,
            member_limit=1,
        )
        subscription.invite_link = limited_link_obj.invite_link
        await subscription.asave(
            update_fields=["invite_link"]
        )
    except TelegramRetryAfter as e:
        await message.answer(
            '🎉 Оплата прошла успешно!',
        )
        await message.answer(
            'Уткнулись в лимиты Telegram! '
            'Отправим ссылку для вступления чуть позже.'
        )
        create_and_send_invite_link_task.apply_async(
            countdown=e.retry_after,
            kwargs=dict(
                user_chat_id=message.from_user.id,
                link_chat_id=settings.PRIVATE_CHANNEL_ID,
                subscription_id=subscription.id,
                member_limit=1,
            )
        )
        return

    builder = InlineKeyboardBuilder()
    builder.button(
        text='🚀 Вступить в приватный канал',
        url=limited_link_obj.invite_link
    )

    await message.answer(
        text='🎉 Оплата прошла успешно!\n\n'
             'Вот твоя индивидуальная ссылка для входа. '
             f'Она сработает <b>только один раз</b> так что никуда её не пересылай.',
        reply_markup=builder.as_markup()
    )



