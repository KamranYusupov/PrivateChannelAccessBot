from datetime import datetime, timedelta
from typing import Optional, Type, Set, Sequence

from django.apps import apps
from django.db import models
from django.db.models import Exists, OuterRef
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from common.typing import ModelT
from web.apps.subscriptions.models import Subscription
from web.db.model_mixins import (
    AbstractTelegramUser,
    TimestampMixin,
)


class TelegramUser(
    AbstractTelegramUser,
    TimestampMixin,
):
    first_name = models.CharField(
        verbose_name=_('Имя'),
        max_length=100,
    )
    last_name = models.CharField(
        verbose_name=_('Фамилия'),
        max_length=100,
        null=True,
        blank=True,
        default=None,
    )
    has_channel_access = models.BooleanField(
        default=False,
        db_index=True,
    )

    @staticmethod
    def _get_subscription_model() -> Optional[Type[ModelT]]:
        return apps.get_model('subscriptions', 'Subscription')

    class Manager(AbstractTelegramUser.Manager):
        def get_telegram_users_with_inactive_subscription(self) -> QuerySet['TelegramUser']:
            Subscription = self._get_subscription_model()
            active_subscription_subquery = Subscription.objects.filter(
                telegram_user_id=OuterRef('pk'),
                is_active=True,
                expires_at__gte=timezone.now(),
            )

            return (
                self
                .annotate(
                    subscription_exists=Exists(active_subscription_subquery),
                )
                .filter(
                    subscription_exists=False,
                    has_channel_access=True,
                )
                .only('id', 'telegram_id')
            )

        def get_telegram_users_with_expires_tomorrow_subscription(self) -> QuerySet['TelegramUser']:
            Subscription = self._get_subscription_model()
            tomorrow = timezone.now() + timedelta(days=1)
            start_of_tomorrow = datetime.combine(tomorrow, datetime.min.time())
            end_of_tomorrow = datetime.combine(tomorrow, datetime.max.time())

            expires_tomorrow_subscription_subquery = Subscription.objects.filter(
                telegram_user_id=OuterRef('pk'),
                is_active=True,
                expires_at__gte=start_of_tomorrow,
                expires_at__lte=end_of_tomorrow,
            )

            return (
                self
                .annotate(
                    expires_tomorrow_subscription_exists=Exists(
                        expires_tomorrow_subscription_subquery
                    ),
                    has_active_subscriptions_after_tomorrow=Exists(
                        Subscription.objects.filter(expires_at__gte=end_of_tomorrow)
                    )
                )
                .filter(
                    expires_tomorrow_subscription_exists=True,
                    has_active_subscriptions_after_tomorrow=False,
                )
                .only('id', 'telegram_id')
            )

    objects = Manager()

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ('-created_at', )
        indexes = [
            models.Index(fields=['telegram_id', 'has_channel_access']),
        ]

    def __str__(self):
        return f'{self.full_name} (ID: {self.telegram_id})'

    @property
    def full_name(self):
        last_name = self.last_name or ''
        return f'{self.first_name} {last_name}'


