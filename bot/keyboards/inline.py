from typing import Dict, Tuple, Optional

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def get_inline_keyboard(*, buttons: Dict[str, str], sizes: Tuple = (1, 2)):
    keyboard = InlineKeyboardBuilder()

    for text, data in buttons.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_invoice_keyboard(
        payment_id: int,
        invoice_url: Optional[str] = None,
):
    if invoice_url:
        pay_button = InlineKeyboardButton(text='Оплатить 💳', url=invoice_url)
    else:
        pay_button = InlineKeyboardButton(text='Оплатить 💳', pay=True)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [pay_button],
            [InlineKeyboardButton(
                text='Отмена ❌',
                callback_data=f'cancel_payment_{payment_id}'
            )]
        ]
    )

    return keyboard

inline_cancel_keyboard = get_inline_keyboard(
    buttons={'Отмена ❌': 'cancel'}
)
