import loguru
from celery import shared_task, Task
from django.conf import settings

from infrastructure.adapters.telegram.client import TelegramBotSyncClient
from infrastructure.adapters.telegram.exceptions import TelegramAPIError
from infrastructure.database.backup import postgres_backup_context
from utils.celery_tasks import execute_with_telegram_retry


@shared_task(
    bind=True,
    max_retries=3,
)
def send_db_backup_task(self: Task) -> None:
    telegram_client = TelegramBotSyncClient()

    try:
        with postgres_backup_context() as backup_file_path:
            with open(backup_file_path, 'rb') as backup_file:
                loguru.logger.info(str(settings.DB_BACKUPS_CHAT_ID))
                execute_with_telegram_retry(
                    task=self,
                    telegram_bot_method=telegram_client.send_document,
                    telegram_bot_method_kwargs={
                        'chat_id': settings.DB_BACKUPS_CHAT_ID,
                        'files': {'document': backup_file},
                    }
                )
                loguru.logger.info('DB backup sent successfully')

    except TelegramAPIError as e:
        loguru.logger.error(f'Error during sending db backup: {e}')
