from django.contrib import admin

from web.apps.payments.models import Payment


@admin.register(Payment)
class AdminPayment(admin.ModelAdmin):
    pass