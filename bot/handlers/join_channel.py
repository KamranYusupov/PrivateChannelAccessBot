import loguru
from aiogram import Router, F
from aiogram.types import ChatJoinRequest

from web.apps.subscriptions.models import Subscription
from web.apps.telegram_users.models import TelegramUser
from web.db.orm_utils import aget_or_none

router = Router()


@router.chat_join_request()
async def face_control_handler(join_request: ChatJoinRequest):
    current_user = await aget_or_none(
        TelegramUser.objects
        .only('id', 'has_channel_access').all(),
        telegram_id=join_request.from_user.id
    )
    if not current_user:
        await join_request.decline()
        return

    user_id = join_request.from_user.id

    has_active_subscription = await (
        Subscription.objects
        .ahas_active_subscription(
            telegram_user_id=current_user.id
        )
    )

    if not has_active_subscription:
        await join_request.decline()

        await join_request.bot.send_message(
            chat_id=user_id,
            text='Сначала купи подписку в боте!',
        )
        return

    if not current_user.has_channel_access:
        current_user.has_channel_access = True
        await current_user.asave(update_fields=['has_channel_access'])

    await join_request.approve()