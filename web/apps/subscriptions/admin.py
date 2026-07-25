from django.contrib import admin

from web.apps.subscriptions.models import Subscription, PrivateChannelTariff


@admin.register(Subscription)
class AdminSubscription(admin.ModelAdmin):
    pass


@admin.register(PrivateChannelTariff)
class AdminPrivateChannelTariff(admin.ModelAdmin):
    pass