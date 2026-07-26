from django.db import models
from django.utils.translation import gettext_lazy as _

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
        related_name='subscription',
        verbose_name=_('Пользователь Telegram'),
    )
    payment = models.OneToOneField(
        'payments.Payment',
        on_delete=models.PROTECT,
        related_name='subscription',
        verbose_name=_('Платеж')
    )
    invite_link = models.URLField(
        blank=True,
        null=True,
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
        return f'Подписка для {self.telegram_user.username or self.telegram_user.telegram_id}'


class PrivateChannelTariff(AbstractTariff, TimestampMixin):
    term_days = models.PositiveIntegerField(
        verbose_name=_('Срок в днях'),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _('Тариф доступа в приватку')
        verbose_name_plural = _('Тарифы доступа в приватку')

    def __str__(self):
        return f'Тариф доступа в приватку на {self.term_days} дней'