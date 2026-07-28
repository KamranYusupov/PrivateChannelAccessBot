from typing import Callable, Awaitable, Any

import loguru
from aiogram import Router, types, F, html

from bot.keyboards.inline import get_inline_keyboard
from services.infra.choices.product_type import (
    product_type_helper,
)
from web.apps.payments.models import ProductType

router = Router()


@router.message(F.text.in_(ProductType.labels))
async def choice_product_type_message_handler(
        message: types.Message,
):
    product_type = product_type_helper.get_choice_by_label(
        message.text
    )
    await choice_product_type_handler(
        message_method=message.answer,
        product_type=product_type
    )


@router.callback_query(F.data.in_(ProductType.labels))
async def choice_product_type_callback_handler(
        callback: types.CallbackQuery,
):
    product_type = product_type_helper.get_choice_by_label(
        callback.data
    )
    await choice_product_type_handler(
        message_method=callback.message.edit_text,
        product_type=product_type
    )


async def choice_product_type_handler(
        message_method: Callable[..., Awaitable[Any]],
        product_type: ProductType,
):
    if not product_type:
        return

    if product_type in (ProductType.FACE_RATE.value, ProductType.CONSULTATION.value):
        await message_method('Функционал в разработке!')
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
    await message_method(
        'Выбери тариф 👇',
        reply_markup=get_inline_keyboard(
            buttons=inline_buttons,
            sizes=sizes,
        )
    )