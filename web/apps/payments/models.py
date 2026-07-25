from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import AsyncBaseModel, TimestampMixin


class MerchantType(models.TextChoices):
    CRYPTO_BOT = 'CryptoBot'
    YKASSA = 'ЮKassa'
    STARS = 'Telegram Stars'


class ProductType(models.TextChoices):
    FACE_RATE = 'Рейт лица'
    PRIVATE_CHANNEL_ACCESS = 'Доступ в приватку'
    CONSULTATION = 'Консультация'


class Payment(AsyncBaseModel, TimestampMixin):
    """Модель платежа (транзакции)"""

    amount = models.DecimalField(
        max_digits=20,
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
        db_index=True,
        verbose_name=_('Тип покупки'),
    )
    merchant_type = models.CharField(
        max_length=20,
        choices=MerchantType.choices,
        db_index=True,
        verbose_name=_('Мерчант'),
    )

    class Meta:
        verbose_name = _('Платеж')
        verbose_name_plural = _('Платежи')
        ordering = ['-created_at']

    def __str__(self):
        created_at_str = self.created_at.strftime('%H:%M %d.%m.%Y')
        return (
            f'Платеж ({self.merchant_type}) - {self.amount} '
            f'| {created_at_str}'
        )