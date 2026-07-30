from datetime import timedelta, datetime
from typing import Optional, List, Set, Type

from asgiref.sync import sync_to_async, async_to_sync
from django.db import models
from django.db.models import OuterRef, Exists
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.apps import apps

from common.typing import ModelT
from web.db.model_mixins import TimestampMixin, AbstractTariff


class Subscription(models.Model):
    tariff = models.ForeignKey(
        'subscriptions.PrivateChannelTariff',
        db_index=True,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name=_('Тариф'),
    )
    telegram_user = models.ForeignKey(
        'telegram_users.TelegramUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='subscriptions',
        verbose_name=_('Пользователь Telegram'),
    )
    payment = models.OneToOneField(
        'payments.Payment',
        on_delete=models.PROTECT,
        related_name='subscription',
        verbose_name=_('Платеж')
    )
    is_active = models.BooleanField(
        _('Активна ли подписка'),
        db_index=True,
        default=True,
    )
    start_at = models.DateTimeField(
        _('Дата начала подписки'),
        auto_now_add=True,
    )
    expires_at = models.DateTimeField(
        _('Дата окончания подписки'),
        db_index=True,
        null=True,
        blank=True,
    )

    def get_telegram_user_model(self) -> Optional[Type[ModelT]]:
        return apps.get_model('telegram_users', 'TelegramUser')

    class Manager(models.Manager):

        def has_active_subscription(
                self,
                telegram_user_id: int,
        ) -> bool:
            return async_to_sync(
                self.ahas_active_subscription
            )(telegram_user_id)

        async def ahas_active_subscription(
                self,
                telegram_user_id: int,
        ) -> bool:
            return await (
                self
                .filter(
                    telegram_user_id=telegram_user_id,
                    is_active=True,
                    expires_at__gte=timezone.now(),
                )
                .aexists()
            )

        async def aget_expires_in_days(self, telegram_user_id: int) -> int:
            result = await (
                self.select_related('tariff')
                .only('tariff__term_days')
                .filter(
                    telegram_user_id=telegram_user_id,
                    expires_at__gte=timezone.now(),
                    is_active=True,
                ).aaggregate(
                    expires_in_days=Coalesce(Sum('tariff__term_days'), 0),
                )
            )
            return result['expires_in_days']

        def get_expires_in_days(self, telegram_user_id: int) -> int:
            return async_to_sync(self.aget_expires_in_days)(telegram_user_id)

        def get_expired_and_active(self, now: datetime = timezone.now()) -> QuerySet:
            return (
                self
                .select_related('telegram_user')
                .only('id', 'telegram_user__telegram_id')
                .filter(
                    is_active=True,
                    expires_at__lt=now,
                )
            )

        def get_expires_tomorrow_subscription(
                self,
                telegram_user_id: int,
        ) -> bool:
            tomorrow = timezone.now() + timedelta(days=1)
            start_of_tomorrow = datetime.combine(tomorrow, datetime.min.time())
            end_of_tomorrow = datetime.combine(tomorrow, datetime.max.time())

            expires_tomorrow_subscription_exists = self.filter(
                telegram_user_id=telegram_user_id,
                is_active=True,
                expires_at__gte=start_of_tomorrow,
                expires_at__lte=end_of_tomorrow,
            ).exists()
            has_active_subscriptions_after_tomorrow = self.filter(
                telegram_user_id=telegram_user_id,
                expires_at__gte=end_of_tomorrow,
            ).exists()
            return expires_tomorrow_subscription_exists and not has_active_subscriptions_after_tomorrow


    objects = Manager()

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        indexes = [
            models.Index(fields=['telegram_user', 'is_active']),
        ]

    def __str__(self):
        return f'Подписка для {self.telegram_user.username or self.telegram_user.telegram_id}'


class PrivateChannelTariff(AbstractTariff, TimestampMixin):
    term_days = models.PositiveIntegerField(
        verbose_name=_('Срок в днях'),
        blank=True,
        null=True,
    )

    class Manager(models.Manager):
        def get_term_days_by_id(self, tariff_id: int) -> Optional[int]:
            tariff = self.filter(id=tariff_id).only('term_days').first()
            return tariff.term_days if tariff else None

        @sync_to_async
        def aget_term_days_by_id(self, tariff_id: int) -> Optional[int]:
            return self.get_term_days_by_id(tariff_id)

    objects = Manager()

    class Meta:
        verbose_name = _('Тариф доступа в приватку')
        verbose_name_plural = _('Тарифы доступа в приватку')

    def __str__(self):
        return f'Тариф доступа в приватку на {self.term_days} дней'