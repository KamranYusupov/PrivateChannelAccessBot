from aiogram import Router, types
from aiogram.filters import CommandStart

from bot.keyboards.reply import get_reply_keyboard
from bot.schemas.telegram_user import TelegramUserCreateSchema
from web.apps.payments.models import ProductType
from web.apps.telegram_users.models import TelegramUser

router = Router()


@router.message(CommandStart())
async def start_command_handler(
    message: types.Message,
):
    current_user_exists = await (
        TelegramUser.objects
        .filter(telegram_id=message.from_user.id)
        .aexists()
    )
    if not current_user_exists:
        user_schema = TelegramUserCreateSchema(
            **message.from_user.model_dump()
        )
        current_user = TelegramUser(
            **user_schema.model_dump()
        )
        await current_user.asave()

    buttons = (label for label in ProductType.labels)
    await message.answer(
        f'Привет, {message.from_user.first_name} 👋. '
        'Выбери раздел: ',
        reply_markup=get_reply_keyboard(buttons=buttons)
    )



