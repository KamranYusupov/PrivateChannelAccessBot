from celery import shared_task, Task
from django.conf import settings
from django.db import transaction

from common.texts import private_channel_invite_link_message
from infrastructure.adapters.telegram.client import TelegramBotSyncClient
from infrastructure.adapters.telegram.exceptions import TelegramAPIError, TelegramRetryAfter
from web.apps.subscriptions.models import Subscription
from web.utils.celery_tasks import execute_with_telegram_retry
from web.apps.telegram_users.tasks.infra.message import send_message_task


@shared_task(bind=True)
def create_and_send_invite_link_task(
        self: Task,
        user_chat_id: int,
        link_chat_id: int,
        subscription_id,
        member_limit: int = 1,
):
    subscription = (
        Subscription.objects
        .only('invite_link')
        .get(id=subscription_id)
    )

    if subscription.invite_link:
        return

    telegram_bot_client = TelegramBotSyncClient(settings.BOT_TOKEN)
    invite_link = execute_with_telegram_retry(
        self,
        task_args=(user_chat_id, link_chat_id, subscription_id, member_limit),
        telegram_bot_method=telegram_bot_client.create_chat_invite_link,
        telegram_bot_method_args=(link_chat_id, member_limit),
    )

    updated = Subscription.objects.filter(
        id=subscription_id,
        invite_link__isnull=True
    ).update(invite_link=invite_link)

    if updated:
        send_invite_link_message_task.delay(
            subscription_id
        )


@shared_task
def send_invite_link_message_task(
        subscription_id: int,
) -> None:
    subscription = (
        Subscription.objects
        .select_related('telegram_user')
        .only(
            'is_invite_link_sent',
            'invite_link',
            'telegram_user__telegram_id',
        )
        .get(id=subscription_id)
    )

    if subscription.is_invite_link_sent:
        return

    text = (
        private_channel_invite_link_message
        + f'\n\n{subscription.invite_link}'
    )
    send_invite_link_text_and_set_invite_link_sent_task.delay(
        text,
        subscription.telegram_user.telegram_id,
        subscription_id,
    )


@shared_task(bind=True)
def send_invite_link_text_and_set_invite_link_sent_task(
        self: Task,
        text: str,
        chat_id: int,
        subscription_id: int,
) -> None:
    telegram_bot_client = TelegramBotSyncClient(settings.BOT_TOKEN)
    execute_with_telegram_retry(
        self,
        task_args=(chat_id, text, subscription_id),
        telegram_bot_method=telegram_bot_client.send_message,
        telegram_bot_method_args=(chat_id, text),
    )
    Subscription.objects.filter(
        id=subscription_id,
        is_invite_link_sent=False,
    ).update(
        is_invite_link_sent=True,
    )


