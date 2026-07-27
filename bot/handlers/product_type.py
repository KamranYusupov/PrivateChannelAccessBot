import loguru
from aiogram import Router, types, F, html

from bot.keyboards.inline import get_inline_keyboard
from services.infra.product_type import (
    ProductTypeService,
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
    product_type = ProductTypeService.get_product_type_by_label(
        message.text
    )
    if not product_type:
        return

    if product_type in (ProductType.FACE_RATE.value, ProductType.CONSULTATION.value):
        await message.answer('Функционал в разработке!')
        return

    if product_type != ProductType.PRIVATE_CHANNEL_ACCESS:
        return

    tariff_model = ProductTypeService.get_tariff_model_by_product_type_value(
        product_type.value
    )

    if not product_type.value or not tariff_model:
        return

    tariffs = tariff_model.objects.all()
    inline_buttons = {
        tariff.title: f'{product_type.value}_{tariff.id}'
        async for tariff in tariffs
    }
    sizes = (1,) * len(inline_buttons)
    await message.answer(
        'Выбери тариф 👇',
        reply_markup=get_inline_keyboard(
            buttons=inline_buttons,
            sizes=sizes,
        )
    )