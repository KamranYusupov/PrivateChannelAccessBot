from django.db import models
from django.utils.translation import gettext_lazy as _

from web.db.model_mixins import AsyncBaseModel


class Subscription(AsyncBaseModel):
    telegram_user = models.ForeignKey(
        "telegram_users.TelegramUser",
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name=_('Пользователь Telegram'),
    )
    is_active = models.BooleanField(
        _('Активна ли подписка'),
        default=True,
    )
    start_at = models.DateTimeField(
        _('Дата начала подписки'),
        auto_now_add=True,
    )
    expires_at = models.DateTimeField(
        _('Дата окончания подписки'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')

    def __str__(self):
        return f"Подписка для {self.telegram_user.username or self.telegram_user.telegram_id}"
