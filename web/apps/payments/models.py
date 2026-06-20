from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import AsyncBaseModel, TimestampMixin


class MerchantType(models.TextChoices):
    CRYPTO_BOT = 'CryptoBot', 'CryptoBot'
    YKASSA = 'YKassa', 'ЮKassa'
    STARS = 'Stars', 'Telegram Stars'


class Payment(AsyncBaseModel, TimestampMixin):
    """Модель платежа (транзакции)"""

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        verbose_name=_('Сумма'),
    )
    payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Метаданные'),
    )
    merchant_type = models.CharField(
        max_length=20,
        choices=MerchantType.choices,
        verbose_name=_('Мерчант'),
    )

    subscription = models.OneToOneField(
        'subscriptions.Subscription',
        on_delete=models.SET_NULL,
        null=True,
        related_name='payment',
        verbose_name=_('Подписка'),
    )

    class Meta:
        verbose_name = _('Платеж')
        verbose_name_plural = _('Платежи')
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'Платеж ({self.merchant_type}) - {self.amount} '
            f'| {self.created_at.strftime('%H:%M %d.%m.%Y')}'
        )