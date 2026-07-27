from celery import shared_task, Task
from django.conf import settings

from infrastructure.adapters.telegram.client import TelegramBotSyncClient
from infrastructure.adapters.telegram.exceptions import TelegramAPIError, TelegramRetryAfter
from web.apps.subscriptions.models import Subscription
from web.utils.celery_tasks import execute_with_telegram_retry


@shared_task(bind=True)
def send_message_task(
        self: Task,
        chat_id: int,
        text: int,
) -> None:
    telegram_bot_client = TelegramBotSyncClient(settings.BOT_TOKEN)
    execute_with_telegram_retry(
        self,
        task_args=(chat_id, text),
        telegram_bot_method=telegram_bot_client.send_message,
        telegram_bot_method_args=(chat_id, text),
    )

@shared_task(bind=True)
def delete_message_task(
        self: Task,
        chat_id: int,
        message_id: int,
) -> None:
    telegram_bot_client = TelegramBotSyncClient(settings.BOT_TOKEN)
    execute_with_telegram_retry(
        self,
        task_args=(chat_id, message_id),
        telegram_bot_method=telegram_bot_client.delete_message,
        telegram_bot_method_args=(chat_id, message_id),
    )

