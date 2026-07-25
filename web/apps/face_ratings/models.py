from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import AsyncBaseModel, TimestampMixin


class FaceRate(AsyncBaseModel, TimestampMixin):
    """Модель оценки лица"""

    title = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name=_('Название'),
    )
    description = models.TextField(_('Описание'))
    price = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        verbose_name=_('Цена'),
    )

    telegram_user = models.ForeignKey(
        'telegram_users.TelegramUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='face_ratings',
        verbose_name=_('Пользователь Telegram'),
    )
    payment = models.OneToOneField(
        'payments.Payment',
        on_delete=models.PROTECT,
        related_name='face_rate',
        verbose_name=_('Платеж,')
    )


class FaceRatePhoto(AsyncBaseModel):
    face_rate = models.ForeignKey(
        'face_ratings.FaceRate',
        on_delete=models.CASCADE,
        related_name='photos',
    )
    photo = models.ImageField(_('Фото'))