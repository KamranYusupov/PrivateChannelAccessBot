import loguru
from aiogram import Router, types, F, html
from aiogram.filters import CommandStart, Command
from aiogram.types import LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.inline import get_inline_keyboard
from bot.keyboards.reply import get_reply_keyboard
from bot.loader import bot
from web.apps.payments.models import ProductType
from web.core import settings

router = Router()


@router.message(CommandStart())
async def start_command_handler(
    message: types.Message,
):
    buttons = (label for label in ProductType.labels)

    await message.answer(
        f'Привет, {message.from_user.first_name} 👋.'
        'Выбери раздел.',
        reply_markup=get_reply_keyboard(buttons=buttons)
    )



