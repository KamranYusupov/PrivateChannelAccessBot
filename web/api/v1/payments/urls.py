from django.urls import include, path

urlpatterns = [
    path('crypto-bot/', include('web.api.v1.payments.crypto_bot.urls')),
]
