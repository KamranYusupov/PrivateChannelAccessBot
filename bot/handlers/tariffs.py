import loguru
from aiogram import Router, types, F, html

from bot.keyboards.inline import get_inline_keyboard
from bot.services.product_callback import (
    ProductCallbackService,
    ProductType,
)
from bot.utils.texts import get_product_text
from web.apps.consultations.models import ConsultationTariff
from web.apps.face_rates.models import FaceRateTariff
from web.apps.payments.models import ProductType
from web.apps.subscriptions.models import PrivateChannelTariff

router = Router()

@router.callback_query(F.data.startswith(ProductType.FACE_RATE.value))
@router.callback_query(F.data.startswith(ProductType.CONSULTATION.value))
@router.callback_query(F.data.startswith(
    ProductType.PRIVATE_CHANNEL_ACCESS.value
))
async def product_tariff_info_handler(
    callback: types.CallbackQuery,
):
    callback_data = callback.data.split('_')
    product_type_value, tariff_id = callback_data

    product_type_label = ProductCallbackService.get_product_type_label_by_value(
        product_type_value
    )

    if not product_type_label:
        return

    tariff_model = ProductCallbackService.get_tariff_model_by_product_type_label(
        product_type_label
    )

    tariff = await tariff_model.objects.aget(
        id=tariff_id,
    )
    if not tariff:
        return

    message_text = get_product_text(
        title=tariff.title,
        price=tariff.price,
        description=tariff.description,
    )

    await callback.message.edit_text(
        message_text,
        reply_markup=get_inline_keyboard(
            buttons={
                'Преобрести 💸': f'buy_{product_type_value}_{tariff_id}',
            },
        )
    )