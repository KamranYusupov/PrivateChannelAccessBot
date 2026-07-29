from celery import shared_task

from infrastructure.adapters.telegram.client import TelegramBotSyncClient


@shared_task
def ban_chat_member_task(
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
