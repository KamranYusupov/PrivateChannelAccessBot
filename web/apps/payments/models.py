from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import TimestampMixin


class MerchantType(models.TextChoices):
    CRYPTO_BOT = 'crypto-bot', 'USDT (CryptoBot)'
    YKASSA = 'ykassa', 'Банковской Картой (ЮKassa)'
    # STARS = 'starts', 'Telegram Stars'


class ProductType(models.TextChoices):
    PRIVATE_CHANNEL_ACCESS = 'private-channel', '🔐 Доступ в приватку'
    FACE_RATE = 'face-rate', '🗿📐 Рейт лица'
    CONSULTATION = 'consultation', '🧠👨‍💻 Личная работа или связзь с мартином (дорого!)'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Ожидает оплаты'
    SUCCESS = 'success', 'Успешно'
    EXPIRED = 'expired', 'Истек'
    CANCELED = 'canceled', 'Отменен'

class Payment(TimestampMixin):
    """Модель платежа (транзакции)"""

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        verbose_name=_('Сумма'),
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        verbose_name=_('Статус'),
    )
    expires_at = models.DateTimeField(
        db_index=True,
        verbose_name=_('Истекает'),
    )
    invoice_message_id = models.IntegerField(
        _('ID сообщения платежа'),
        default=None,
        null=True,
        blank=True,
    )
    product_type = models.CharField(
        max_length=25,
        choices=ProductType.choices,
        db_index=True,
        verbose_name=_('Тип покупки'),
    )
    merchant_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Метаданные'),
    )
    merchant_type = models.CharField(
        max_length=20,
        choices=MerchantType.choices,
        db_index=True,
        verbose_name=_('Мерчант'),
    )
    merchant_payment_id = models.CharField(
        max_length=100,
        db_index=True,
        unique=True,
        verbose_name=_('ID Платежа мерчанта'),
        null=True,
        default=None,
        blank=True,
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
