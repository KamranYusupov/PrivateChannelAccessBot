from celery import shared_task, Task

from infrastructure.adapters.telegram.client import TelegramBotSyncClient
from web.core.redis_init import telegram_api_task_rate_limit


@shared_task(bind=True, max_retries=5)
@telegram_api_task_rate_limit()
def ban_chat_member_task(
        self: Task,
        user_id: int,
        chat_id: int,
        until_date: int | None = None,
        revoke_messages: bool = False,
) -> None:
    telegram_client = TelegramBotSyncClient()
    telegram_client.ban_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        until_date=until_date,
        revoke_messages=revoke_messages,
    )
