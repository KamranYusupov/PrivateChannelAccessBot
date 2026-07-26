from django.db import models
from django.utils.translation import gettext_lazy as _

        
class AbstractTelegramUser(models.Model):
    telegram_id = models.BigIntegerField(
        verbose_name=_('Телеграм ID'),
        unique=True,
        db_index=True,
    )
    username = models.CharField(
        _('Имя пользователя'),
        max_length=70,
        unique=True,
        db_index=True,
        null=True,
    )
    
    class Meta: 
        abstract = True
    
    
class TimestampMixin(models.Model):
    created_at = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Дата последнего обновления'),
        auto_now=True
    )

    class Meta:
        abstract = True


class AbstractTariff(models.Model):
    title = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name=_('Название'),
    )
    description = models.TextField(_('Описание'))
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Цена'),
    )

    class Meta:
        verbose_name = _('Тариф')
        verbose_name_plural = _('Тарифы')
        abstract = True

    def __str__(self):
        return self.title
