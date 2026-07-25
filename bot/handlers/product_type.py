import loguru
from aiogram import Router, types, F, html

from bot.keyboards.inline import get_inline_keyboard
from bot.services.product_callback import (
    ProductCallbackService,
)
from web.apps.consultations.models import ConsultationTariff
from web.apps.face_rates.models import FaceRateTariff
from web.apps.payments.models import ProductType
from web.apps.subscriptions.models import PrivateChannelTariff

router = Router()

@router.message(F.text.in_(ProductType.labels))
async def choice_product_type(
        message: types.Message,
):
    product_type_value = ProductCallbackService.get_product_type_value_by_label(
        message.text
    )
    if product_type_value in (ProductType.FACE_RATE.value, ProductType.CONSULTATION.value):
        await message.answer('Функционал в разработке!')
        return

    product_type_value = ProductCallbackService.get_product_type_value_by_label(
        message.text
    )
    if not product_type_value:
        return
    tariff_model = ProductCallbackService.get_tariff_model_by_product_type_value(
        product_type_value
    )

    if not product_type_value or not tariff_model:
        return

    tariffs = await tariff_model.objects.a_all()
    inline_buttons = {
        tariff.title: f'{product_type_value}_{tariff.id}'
        for tariff in tariffs
    }
    sizes = (1,) * len(inline_buttons)
    await message.answer(
        'Выбери тариф 👇',
        reply_markup=get_inline_keyboard(
            buttons=inline_buttons,
            sizes=sizes,
        )
    )