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

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ("-created_at", )

    def __str__(self):
        return f"{self.full_name} (ID: {self.telegram_id})"

    @property
    def full_name(self):
        last_name = self.last_name or ""
        return f"{self.first_name} {last_name}"


