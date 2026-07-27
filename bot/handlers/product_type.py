import loguru
from aiogram import Router, types, F, html

from bot.keyboards.inline import get_inline_keyboard
from services.infra.choices.product_type import (
    product_type_helper,
)
from web.apps.payments.models import ProductType

router = Router()

@router.message(F.text.in_(ProductType.labels))
async def choice_product_type(
        message: types.Message,
):
    product_type = product_type_helper.get_choice_by_label(
        message.text
    )
    if not product_type:
        return

    if product_type in (ProductType.FACE_RATE.value, ProductType.CONSULTATION.value):
        await message.answer('Функционал в разработке!')
        return

    if product_type != ProductType.PRIVATE_CHANNEL_ACCESS:
        return

    tariff_model = product_type_helper.get_tariff_model_by_value(
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