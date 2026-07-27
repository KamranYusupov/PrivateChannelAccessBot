from django.urls import path

from web.api.v1.payments.crypto_bot import views

urlpatterns = [
    path('webhook/', views.update_webhook, name='crypto-bot-webhook'),
]