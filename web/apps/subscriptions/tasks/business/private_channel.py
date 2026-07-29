import time
from typing import List

import loguru
from aiogram.types import InlineKeyboardMarkup
from celery import shared_task, Task
from celery_once import QueueOnce
from django.conf import settings

from infrastructure.adapters.telegram.client import TelegramBotSyncClient
from infrastructure.adapters.telegram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest, TelegramRetryAfter, TelegramForbidden,
)
from web.apps.payments.models import ProductType
from web.apps.subscriptions.models import Subscription
from web.apps.telegram_users.tasks import send_message_task
from web.utils.celery_tasks import execute_with_telegram_retry


@shared_task(
    bind=True,
    max_retries=5,
    base=QueueOnce,
    once={'keys': [], 'unlock_before_retry': True}
)
def set_subscriptions_inactive_and_kick_users_task(
        self: Task,
        batch_size: int = 20
):
    expired_subscriptions = Subscription.objects.get_expired_and_active()
    telegram_client = TelegramBotSyncClient()
    default_exc_msg = (
        'Error while kicking {telegram_id}: "{error}"'
    )

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
                default_exc_msg.format(
                    telegram_id=telegram_id,
                    error=e,
                )
            )

        except TelegramRetryAfter as e:
            if kicked_subs_ids:
                (Subscription.objects
                 .filter(id__in=kicked_subs_ids)
                 .update(is_active=False))
            loguru.logger.warning(
                f'Retrying kicking user {telegram_id} '
                f'after {e.retry_after} seconds'
            )
            self.retry(countdown=e.retry_after + 2)

        except TelegramAPIError as e:
            loguru.logger.info(
                default_exc_msg.format(
                    telegram_id=telegram_id,
                    error=e,
                )
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


@shared_task(
    bind=True,
    max_retries=5,
    base=QueueOnce,
    once={'keys': [], 'unlock_before_retry': True}

)
def mass_mailing_expires_tomorrow_subscription_task(
        self: Task,
        expires_tomorrow_telegram_ids: List[int] | None = None,
):
    if not expires_tomorrow_telegram_ids:
        expires_tomorrow_telegram_ids = Subscription.objects.get_expires_tomorrow_telegram_ids()

    failed_to_send_message_ids = []
    telegram_client = TelegramBotSyncClient()

    default_exc_msg = (
        'Error while sending message to {telegram_id}: "{error}"'
    )
    inline_keyboard = [{
        'text': '💰 Продлить подписку',
        'callback_data': ProductType.PRIVATE_CHANNEL_ACCESS.label,
    }]
    text = '⚠ До конца подписки остался 1 день! ️⚠'

    for index, telegram_id in enumerate(expires_tomorrow_telegram_ids):
        need_to_retry = True
        try:
            telegram_client.send_message(
                chat_id=telegram_id,
                text=text,
                reply_markup={'inline_keyboard': inline_keyboard},
            )
            need_to_retry = False
        except (TelegramBadRequest, TelegramForbidden) as e:
            need_to_retry = False
            exc_msg = default_exc_msg.format(
                telegram_id=telegram_id,
                error=e,
            )
            loguru.logger.info(exc_msg)

        except TelegramRetryAfter as e:
            loguru.logger.warning(
                f'Retrying sendMessage to {telegram_id} '
                f'after {e.retry_after} seconds'
            )
            failed_to_send_message_ids += (
                expires_tomorrow_telegram_ids[index:]
            )
            self.retry(
                kwargs={
                    'expires_tomorrow_telegram_ids': \
                        failed_to_send_message_ids
                },
                countdown=e.retry_after + 1,
            )

        except TelegramAPIError as e:
            exc_msg = default_exc_msg.format(
                telegram_id=telegram_id,
                error=e,
            )
            loguru.logger.error(exc_msg)

        if need_to_retry:
            failed_to_send_message_ids.append(telegram_id)

        time.sleep(0.04)

    if failed_to_send_message_ids:
        self.retry(
            kwargs={
                'expires_tomorrow_telegram_ids': \
                    failed_to_send_message_ids
            },
        )

