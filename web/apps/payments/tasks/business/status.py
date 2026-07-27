from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from web.apps.payments.models import (
    Payment,
    PaymentStatus,
    MerchantType,
)


@shared_task
def set_expired_payments(
        batch_size: int = 500,
):
    while True:
        ids = list(
            Payment.objects.filter(
                status=PaymentStatus.PENDING,
                expires_at__lte=timezone.now(),
            )
            .values_list("id", flat=True)[:batch_size]
        )

        if not ids:
            break

        Payment.objects.filter(id__in=ids).update(
            status=PaymentStatus.EXPIRED
        )