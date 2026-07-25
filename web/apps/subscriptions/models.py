from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import AsyncBaseModel


class Subscription(AsyncBaseModel):
    tariff = models.ForeignKey(
        'tariffs.PrivateChannelTariff',
        db_index=True,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('Тариф'),
    )
    telegram_user = models.OneToOneField(
        'telegram_users.TelegramUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='subscription',
        verbose_name=_('Пользователь Telegram'),
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

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')

    def __str__(self):
        return f"Подписка для {self.telegram_user.username or self.telegram_user.telegram_id}"
