from typing import Sequence
from datetime import datetime

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from django.utils import timezone


def get_reply_keyboard(
    buttons: Sequence[str],
    resize_keyboard: bool = True,
) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=button_text)] for button_text in buttons]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=resize_keyboard
    )

