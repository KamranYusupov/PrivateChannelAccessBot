from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import AsyncBaseModel, TimestampMixin


class MerchantType(models.TextChoices):
    CRYPTO_BOT = 'CryptoBot'
    YKASSA = 'ЮKassa'
    STARS = 'Telegram Stars'


class ProductType(models.TextChoices):
    FACE_RATE = 'Face Rate'
    PRIVATE_CHANNEL_ACCESS = 'Private Channel Access'
    CONSULTATION = 'Consultation'


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
    product_type = models.CharField(
        max_length=25,
        choices=ProductType.choices,
        verbose_name=_('Тип покупки'),
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