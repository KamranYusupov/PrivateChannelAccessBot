import time

import loguru
from celery import shared_task
from django.conf import settings

from infrastructure.adapters.telegram.client import TelegramBotSyncClient
from infrastructure.adapters.telegram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest, TelegramRetryAfter, TelegramForbidden,
)
from web.apps.subscriptions.models import Subscription

@shared_task
def set_subscriptions_inactive_and_kick_users(
        batch_size: int = 20
):
    expired_subscriptions = Subscription.objects.get_expired_and_active()
    telegram_client = TelegramBotSyncClient()

    kicked_subs_ids = []
    for subscription in expired_subscriptions:
        until_date = int(time.time()) + 60
        telegram_id = subscription.telegram_user.telegram_id
        try:
            telegram_client.ban_chat_member(
                user_id=telegram_id,
                chat_id=settings.PRIVATE_CHANNEL_ID,
                until_date=until_date
            )
            kicked_subs_ids.append(subscription.id)
        except (TelegramBadRequest, TelegramForbidden) as e:
            kicked_subs_ids.append(subscription.id)
            loguru.logger.info(
                f'Error while kicking {telegram_id}: '
                f'"{e.message}"'
            )

        except TelegramRetryAfter as e:
            loguru.logger.warning(
                f'Retrying kicking user {telegram_id} '
                f'after {e.retry_after} seconds'
            )
            time.sleep(e.retry_after + 2)
            continue

        except TelegramAPIError as e:
            loguru.logger.warning(
                f'Error while kicking {telegram_id}: '
                f'"{e.message}"'
            )

        time.sleep(0.04)

        if len(kicked_subs_ids) >= batch_size:
            (Subscription.objects
             .filter(id__in=kicked_subs_ids)
             .update(is_active=False))
            kicked_subs_ids.clear()


    if kicked_subs_ids:
        (Subscription.objects
         .filter(id__in=kicked_subs_ids)
         .update(is_active=False))

