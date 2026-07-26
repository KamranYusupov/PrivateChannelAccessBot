from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import TimestampMixin, AbstractTariff


class FaceRate(TimestampMixin):
    """Модель оценки лица"""

    tariff = models.ForeignKey(
        'face_rates.FaceRateTariff',
        db_index=True,
        on_delete=models.PROTECT,
        related_name='face_rates',
        verbose_name=_('Тариф'),
    )
    telegram_user = models.ForeignKey(
        'telegram_users.TelegramUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='face_rates',
        verbose_name=_('Пользователь Telegram'),
    )
    payment = models.OneToOneField(
        'payments.Payment',
        on_delete=models.PROTECT,
        related_name='face_rate',
        verbose_name=_('Платеж,')
    )

    class Meta:
        verbose_name = _('Рейт')
        verbose_name_plural = _('Рейты')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.tariff} - {self.created_at}'


class FaceRateTariff(AbstractTariff, TimestampMixin):
    """Модель тарифа оценки лица"""



class FaceRatePhoto(models.Model):
    face_rate = models.ForeignKey(
        'face_rates.FaceRate',
        on_delete=models.CASCADE,
        related_name='photos',
    )
    photo = models.ImageField(_('Фото'))