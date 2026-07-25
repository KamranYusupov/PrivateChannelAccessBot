from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import AsyncBaseModel, TimestampMixin


class PrivateChannelTariff(AsyncBaseModel, TimestampMixin):
    title = models.CharField(
        verbose_name=_("Название"),
        max_length=255,
    )
    info_text = models.TextField()
    price = models.DecimalField(
        verbose_name=_('Цена'),
        decimal_places=6,
        max_digits=16,
    )
    term_days = models.PositiveIntegerField(
        verbose_name=_('Срок в днях'),
        blank=True,
        null=True,
    )


