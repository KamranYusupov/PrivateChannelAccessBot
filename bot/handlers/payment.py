import json
from datetime import timedelta
from json import JSONDecodeError

import loguru
from aiogram import Router, types, F
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import LabeledPrice, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import pydantic
from django.conf import settings
from django.utils import timezone

from bot.keyboards.inline import get_inline_keyboard, get_invoice_keyboard
from bot.loader import bot
from bot.utils.bot import delete_message_or_pass
from common.exceptions import PaymentAlreadyProcessed, PaymentExpired
from infrastructure.adapters.crypto_bot.client import CryptoBotAPIClient
from services.infra.choices.merchant_type import merchant_type_helper
from services.infra.choices.product_type import (
    product_type_helper,
)
from services.infra.ykassa_payload import PayloadService
from services.business.payment import PaymentUseCase
from web.apps.payments.models import MerchantType, Payment, PaymentStatus
from web.apps.telegram_users.models import TelegramUser
from web.db.orm_utils import aget_or_none
from web.apps.subscriptions.tasks.business.invite_link import (
    create_and_send_invite_link_task,
)
from web.apps.payments.tasks import update_payment_invoice_message_id_task

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


async def prepare_invoice_handler(
    callback: types.CallbackQuery,
    expires_in: int,
):
    callback_data = callback.data.split('_')
    merchant_type_value = callback_data[0]
    product_type_value, tariff_id = callback_data[-2:]

    merchant_type = merchant_type_helper.get_choice_by_value(
        merchant_type_value,
    )
    tariff_model = product_type_helper.get_tariff_model_by_value(
        product_type_value
    )
    product_type = product_type_helper.get_choice_by_value(
        product_type_value
    )
    if not tariff_model or not product_type or not merchant_type:
        await callback.message.delete()
        return

    tariff = await aget_or_none(tariff_model.objects.all(), id=tariff_id)
    await callback.message.delete()

    if not tariff:
        loguru.logger.error(f'Tariff {tariff_id} not found.')
        await callback.message.delete()
        return

    invoice_payload = {
        'product_type_value': product_type_value,
        'tariff_id': tariff_id,
    }
    loguru.logger.debug(
        f"{product_type} {merchant_type} {invoice_payload}"
    )
    payment = await Payment.objects.acreate(
        amount=tariff.price,
        product_type=product_type,
        merchant_type=merchant_type,
        merchant_payload=invoice_payload,
        expires_at=(
            timezone.now() + timedelta(minutes=expires_in)
        ),
    )
    return payment, tariff

@router.callback_query(
    F.data.startswith(f'{MerchantType.YKASSA.value}_buy')
)
async def send_ykassa_invoice(
    callback: types.CallbackQuery,
):
    result = await prepare_invoice_handler(
        callback=callback,
        expires_in=settings.YKASSA_PAYMENT_EXPIRES_IN_MINUTES,
    )
    if not result:
        return

    payment, tariff = result

    invoice_keyboard = get_invoice_keyboard(payment.id)
    invoice_amount = payment.amount * 100
    invoice_message = await callback.message.answer_invoice(
        title=tariff.title,
        description=tariff.description,
        payload=json.dumps(payment.merchant_payload),
        provider_token=settings.YKASSA_TOKEN,
        reply_markup=invoice_keyboard,
        currency='RUB',
        test=True,
        prices=[LabeledPrice(label=tariff.title, amount=invoice_amount)],
    )
    update_payment_invoice_message_id_task.delay(
        payment.id,
        invoice_message.message_id,
    )


@router.callback_query(
    F.data.startswith(f'{MerchantType.CRYPTO_BOT.value}_buy')
)
async def send_crypto_bot_invoice(
        callback: types.CallbackQuery,
):
    result = await prepare_invoice_handler(
        callback=callback,
        expires_in=settings.CRYPTO_BOT_PAYMENT_EXPIRES_IN_MINUTES,
    )
    if not result:
        return

    await callback.answer('Создаю платеж . . .')

    payment, tariff = result
    crypto_bot_api_client = CryptoBotAPIClient()
    response = await crypto_bot_api_client.create_invoice(
        currency_type='fiat',
        fiat='RUB',
        amount=payment.amount,
        accepted_assets='USDT',
        expires_in=settings.CRYPTO_BOT_PAYMENT_EXPIRES_IN_MINUTES * 60,
    )
    if not response.get('ok'):
        loguru.logger.error(response['error'])
        await callback.message.edit_text(
            'Произошла ошибка при создании платежа. Попробуйте позже.'
        )
        return

    invoice_keyboard = get_invoice_keyboard(
        payment.id,
        invoice_url=response['result']['mini_app_invoice_url']
    )
    invoice_message = await callback.message.answer(
        'Оплатите счет в приложении ⤵️',
        reply_markup=invoice_keyboard
    )

    update_payment_invoice_message_id_task.delay(
        payment.id,
        invoice_message.message_id,
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(
        pre_checkout_query: types.PreCheckoutQuery,
):
    try:
        invoice_payload_schema = PayloadService.get_invoice_payload_schema(
            pre_checkout_query.invoice_payload,
        )
    except (pydantic.ValidationError, JSONDecodeError):
        await pre_checkout_query.bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=False,
            error_message='Ошибка данных. Попробуйте еще раз.',
        )
        return

    tariff_model = product_type_helper.get_tariff_model_by_value(
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

    payment = await aget_or_none(
        Payment.objects.all(),
        id=invoice_payload_schema.payment_id,
    )

    if not payment:
        await pre_checkout_query.answer(
            ok=False,
            error_message='Ошибка данных. Платеж не найден.'
        )
        return

    if payment.status == PaymentStatus.EXPIRED:
        await pre_checkout_query.answer(
            ok=False,
            error_message='Платеж истек. Создайте новый.'
        )
        return

    if payment.status == PaymentStatus.CANCELED:
        await pre_checkout_query.answer(
            ok=False,
            error_message='Платеж был отменен. Создайте новый.'
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
        invoice_payload_schema = PayloadService.get_invoice_payload_schema(
            message.successful_payment.invoice_payload,
        )
    except (pydantic.ValidationError, JSONDecodeError):
        await message.answer(data_error_msg)
        return

    product_type = product_type_helper.get_choice_by_value(
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
    try:
        subscription, payment = await PaymentUseCase.aexecute(
            telegram_user_id=telegram_user_id,
            payment_id=invoice_payload_schema.payment_id,
            tariff_id=invoice_payload_schema.tariff_id,
            merchant_payment_id=message.successful_payment.provider_payment_charge_id,
            product_type=product_type,
        )
    except Payment.DoesNotExist:
        await message.answer(data_error_msg)
        return
    except PaymentAlreadyProcessed:
        return

    await delete_message_or_pass(
        bot,
        chat_id=message.from_user.id,
        message_id=payment.invoice_message_id,
    )

    try:
        limited_link_obj = await message.bot.create_chat_invite_link(
            chat_id=settings.PRIVATE_CHANNEL_ID,
            member_limit=1,
        )
        subscription.invite_link = limited_link_obj.invite_link
        await subscription.asave(
            update_fields=['invite_link']
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


@router.callback_query(F.data.startswith('cancel_payment_'))
async def cancel_payment_handler(
    callback: types.CallbackQuery,
):
    payment_id = callback.data.split('_')[-1]
    updated = await Payment.objects.filter(
        id=payment_id,
        status=PaymentStatus.PENDING
    ).aupdate(status=PaymentStatus.CANCELED)

    await callback.message.delete()

    if updated > 0:
        await callback.message.answer(
            'Платеж успешно закрыт ✅',
            reply_markup=None,
        )
        return

    payment = await aget_or_none(Payment.objects.all(), id=payment_id)

    if payment and payment.status == PaymentStatus.SUCCESS:
        await callback.message.answer('Чек уже оплачен ✅', reply_markup=None)
    else:
        await callback.message.answer('Чек уже недействителен.', reply_markup=None)
