from typing import Sequence
from datetime import datetime

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from django.utils import timezone

from web.apps.payments.models import ProductType


def get_reply_keyboard(
    buttons: Sequence[str],
    resize_keyboard: bool = True,
) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=button_text)] for button_text in buttons]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=resize_keyboard
    )


def get_base_reply_keyboard() -> ReplyKeyboardMarkup:
    buttons = ('📱 Моя подписка', )
    buttons += tuple(label for label in ProductType.labels)

    return get_reply_keyboard(buttons)
