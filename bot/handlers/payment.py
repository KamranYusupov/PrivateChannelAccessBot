import json

import loguru
from aiogram import Router, types, F, html
from aiogram.types import LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.exceptions import ObjectDoesNotExist

from bot.keyboards.inline import get_inline_keyboard
from bot.services.product_callback import (
    ProductCallbackService,
)
from bot.utils.texts import get_product_text
from web.apps.consultations.models import ConsultationTariff
from web.apps.face_rates.models import FaceRateTariff
from web.apps.payments.models import ProductType, MerchantType
from web.apps.subscriptions.models import PrivateChannelTariff
from web.core import settings

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

    try:
        tariff = await tariff_model.objects.aget(id=tariff_id)
    except ObjectDoesNotExist:
        return
    finally:
        await callback.message.delete()

    amount = int(tariff.price) * 100
    invoice_payload = {
        "product_type": product_type_value,
        "tariff_id": tariff_id,
    }
    await callback.message.answer_invoice(
        title=tariff.title,
        description=tariff.description,
        payload=json.dumps(invoice_payload),
        provider_token=settings.YKASSA_TOKEN,
        currency="RUB",
        test=True,
        prices=[LabeledPrice(label=tariff.title, amount=amount)],
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(
        pre_checkout_query: types.PreCheckoutQuery,
):
    await pre_checkout_query.bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True,
    )


@router.message(F.successful_payment)
async def successful_payment(
        message: types.Message,
):
    payload = message.successful_payment.invoice_payload

    try:
        limited_link_obj = await message.bot.create_chat_invite_link(
            chat_id=settings.PRIVATE_CHANNEL_ID,
            member_limit=1,
        )

        builder = InlineKeyboardBuilder()
        builder.button(
            text="🚀 Вступить в приватный канал",
            url=limited_link_obj.invite_link
        )

        await message.answer(
            text="🎉 Оплата прошла успешно!\n\n"
                 "Вот твоя индивидуальная ссылка для входа. "
                 f"Она сработает <b>только один раз</b> так что никуда её не пересылай.",
            reply_markup=builder.as_markup()
        )

    except Exception as e:
        loguru.logger.error(f"Ошибка при выдаче ссылки юзеру: {e}")
        await message.answer(
            "Оплата прошла, но возникла ошибка с выдачей ссылки. "
            "Пожалуйста, напиши в поддержку!"
        )




