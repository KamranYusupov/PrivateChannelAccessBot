from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import AsyncBaseModel, TimestampMixin, TariffMixin


class Consultation(AsyncBaseModel, TimestampMixin):
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

class ConsultationTariff(AsyncBaseModel, TariffMixin, TimestampMixin):
    """Модель тарифа оценки лица"""
