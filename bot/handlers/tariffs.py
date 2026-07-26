import loguru
from aiogram import Router, types, F, html
from django.core.exceptions import ObjectDoesNotExist

from bot.keyboards.inline import get_inline_keyboard
from services.infra.product_callback import (
    ProductCallbackService,
    ProductType,
)
from bot.utils.texts import get_product_text
from web.apps.consultations.models import ConsultationTariff
from web.apps.face_rates.models import FaceRateTariff
from web.apps.payments.models import ProductType
from web.apps.subscriptions.models import PrivateChannelTariff
from web.db.orm_utils import aget_or_none

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

    tariff_model = ProductCallbackService.get_tariff_model_by_product_type_value(
        product_type_value
    )

    tariff = await aget_or_none(tariff_model.objects.all(), id=tariff_id)
    if not tariff:
        await callback.message.delete()
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