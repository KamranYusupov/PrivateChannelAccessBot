import time
from collections import defaultdict
from typing import List

import loguru
from aiogram.types import InlineKeyboardMarkup
from celery import shared_task, Task
from celery_once import QueueOnce, AlreadyQueued
from django.conf import settings
from django.db.models.query import QuerySet
from django.utils import timezone

from infrastructure.adapters.telegram.client import TelegramBotSyncClient
from infrastructure.adapters.telegram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest, TelegramRetryAfter, TelegramForbidden,
)
from utils.celery_tasks import execute_with_telegram_retry, delay_excepting_already_queued
from utils.orm import update_by_batches
from web.apps.payments.models import ProductType
from web.apps.subscriptions.models import Subscription
from web.apps.telegram_users.models import TelegramUser
from web.apps.telegram_users.tasks import send_message_task
from web.core.redis_init import telegram_api_task_rate_limit


@shared_task(
    bind=True,
    base=QueueOnce,
    once={'keys': [], 'unlock_before_retry': True}
)
def deactivate_subscriptions_task(
        self: Task,
        batch_size: int = 500
) -> int:
    return update_by_batches(
        manager=Subscription.objects,
        filters=dict(
            is_active=True,
            expires_at__lt=timezone.now()
        ),
        update_kwargs={'is_active': False},
        batch_size=batch_size,
    )


@shared_task(
    base=QueueOnce,
    once={'keys': [], 'unlock_before_retry': True}
)
def mass_kick_telegram_users_from_channel_with_inactive_subscription_task():
    telegram_users_with_inactive_subscription = (
        TelegramUser.objects
        .get_telegram_users_with_inactive_subscription()
    )

    for telegram_user in telegram_users_with_inactive_subscription:
        inline_keyboard = [[{
            'text': '💰 Тарифы',
            'callback_data': ProductType.PRIVATE_CHANNEL_ACCESS.label,
        }]]
        delay_excepting_already_queued(
            task=send_message_task,
            kwargs={
                'text': 'Ваша подписка кончилась!',
                'chat_id': telegram_user.telegram_id,
                'reply_markup': {'inline_keyboard': inline_keyboard}
            }
        )
        delay_excepting_already_queued(
            task=kick_telegram_user_from_channel,
            kwargs={
                'telegram_user_id': telegram_user.id,
                'telegram_id': telegram_user.telegram_id,
            }
        )



@shared_task(
    bind=True,
    max_retries=1000,
    base=QueueOnce,
    once={'keys': ['telegram_id'], 'unlock_before_retry': False}
)
@telegram_api_task_rate_limit()
def kick_telegram_user_from_channel(
        self: Task,
        telegram_user_id: int,
        telegram_id: int,
) -> None:
    has_active_subscription = Subscription.objects.filter(
        telegram_user_id=telegram_user_id,
        is_active=True,
        expires_at__gte=timezone.now(),
    ).exists()

    if has_active_subscription:
        return

    telegram_client = TelegramBotSyncClient()
    default_exc_msg = (
        'Error while kicking {telegram_id}: "{error}"'
    )
    until_date = int(time.time()) + 60
    kick_success = False

    try:
        execute_with_telegram_retry(
            task=self,
            telegram_bot_method=telegram_client.ban_chat_member,
            telegram_bot_method_kwargs={
                'user_id': telegram_id,
                'chat_id': settings.PRIVATE_CHANNEL_ID,
                'until_date': until_date
            }
        )
        execute_with_telegram_retry(
            task=self,
            telegram_bot_method=telegram_client.unban_chat_member,
            telegram_bot_method_kwargs={
                'user_id': telegram_id,
                'chat_id': settings.PRIVATE_CHANNEL_ID,
                'only_if_banned': True
            }
        )

        kick_success = True
    except (TelegramBadRequest, TelegramForbidden) as e:
        loguru.logger.info(
            default_exc_msg.format(
                telegram_id=telegram_id,
                error=e,
            )
        )
        kick_success = True

    except TelegramAPIError as e:
        loguru.logger.info(
            default_exc_msg.format(
                telegram_id=telegram_id,
                error=e,
            )
        )

    if kick_success:
        TelegramUser.objects.filter(
            telegram_id=telegram_id,
        ).update(has_channel_access=False)


@shared_task(
    bind=True,
    max_retries=5,
    base=QueueOnce,
    once={'keys': [], 'unlock_before_retry': True}
)
def mass_mailing_expires_tomorrow_subscription_task(
        self: Task,
):
    expires_tomorrow_telegram_users = (
        TelegramUser.objects
        .get_telegram_users_with_expires_tomorrow_subscription()
    )

    for telegram_user in expires_tomorrow_telegram_users:
        delay_excepting_already_queued(
            task=send_subscription_expires_tomorrow_message_task,
            kwargs={
                'telegram_user_id': telegram_user.id,
                'telegram_id': telegram_user.telegram_id,
            }
        )



@shared_task(
    bind=True,
    max_retries=1000,
    base=QueueOnce,
    once={'keys': ['telegram_id'], 'unlock_before_retry': False}
)
@telegram_api_task_rate_limit()
def send_subscription_expires_tomorrow_message_task(
        self: Task,
        telegram_user_id: int,
        telegram_id: int
):
    expires_tomorrow_subscription = (
        Subscription.objects
        .get_expires_tomorrow_subscription(
            telegram_user_id=telegram_user_id
        )
    )
    if not expires_tomorrow_subscription:
        return

    default_exc_msg = (
        'Error while sending message to {telegram_id}: "{error}"'
    )
    inline_keyboard = [[{
        'text': '💰 Продлить подписку',
        'callback_data': ProductType.PRIVATE_CHANNEL_ACCESS.label,
    }]]
    text = '⚠ До конца подписки остался 1 день ️⚠'
    telegram_client = TelegramBotSyncClient()

    try:
        execute_with_telegram_retry(
            task=self,
            telegram_bot_method=telegram_client.send_message,
            telegram_bot_method_kwargs={
                'chat_id': telegram_id,
                'text': text,
                'reply_markup': {'inline_keyboard': inline_keyboard},
            }
        )
    except (TelegramBadRequest, TelegramForbidden) as e:
        exc_msg = default_exc_msg.format(
            telegram_id=telegram_id,
            error=e,
        )
        loguru.logger.info(exc_msg)

    except TelegramAPIError as e:
        exc_msg = default_exc_msg.format(
            telegram_id=telegram_id,
            error=e,
        )
        loguru.logger.error(exc_msg)



