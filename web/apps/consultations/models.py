from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import TimestampMixin, TariffMixin


class Consultation(models.Model, TimestampMixin):
    """Модель оценки лица"""

    tariff = models.ForeignKey(
        'consultations.ConsultationTariff',
        db_index=True,
        on_delete=models.PROTECT,
        related_name='consultations',
        verbose_name=_('Тариф'),
    )
    telegram_user = models.ForeignKey(
        'telegram_users.TelegramUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='consultations',
        verbose_name=_('Пользователь Telegram'),
    )
    payment = models.OneToOneField(
        'payments.Payment',
        on_delete=models.PROTECT,
        related_name='consultation',
        verbose_name=_('Платеж,')
    )

    class Meta:
        verbose_name = _('Консультация')
        verbose_name_plural = _('Консультации')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.tariff} - {self.created_at}'

class ConsultationTariff(models.Model, TariffMixin, TimestampMixin):
    """Модель тарифа оценки лица"""
