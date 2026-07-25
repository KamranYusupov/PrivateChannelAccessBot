import loguru
from aiogram import Router, types, F, html

from bot.keyboards.inline import get_inline_keyboard
from bot.services.product_callback import (
    ProductCallbackService,
)
from bot.utils.texts import get_product_text
from web.apps.consultations.models import ConsultationTariff
from web.apps.face_rates.models import FaceRateTariff
from web.apps.payments.models import ProductType, MerchantType
from web.apps.subscriptions.models import PrivateChannelTariff

router = Router()

@router.callback_query(F.data.startswith('buy_'))
async def buy_product_tariff(
    callback: types.CallbackQuery,
):
    merchant_type_buttons = {
        merchant_type.label: f'{callback.data}_{merchant_type.value}'
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
    callback_data = callback.data.split('_')
    product_callback_data, tariff_id = callback_data[1:]

    tariff_model = ProductCallbackService.get_tariff_model_by_product_callback_data(
        ProductCallbackDataEnum(product_callback_data)
    )
    tariff = await tariff_model.objects.aget(id=tariff_id)





