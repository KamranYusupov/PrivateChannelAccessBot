from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import (
    AbstractTelegramUser,
    TimestampMixin,
)


class TelegramUser(
    AbstractTelegramUser,
    TimestampMixin,
):
    first_name = models.CharField(
        verbose_name=_("Имя"),
        max_length=100,
    )
    last_name = models.CharField(
        verbose_name=_("Фамилия"),
        max_length=100,
        null=True,
        blank=True,
        default=None,
    )
