from django.contrib import admin

from web.apps.telegram_users.models import TelegramUser


@admin.register(TelegramUser)
class AdminTelegramUser(admin.ModelAdmin):
    pass

