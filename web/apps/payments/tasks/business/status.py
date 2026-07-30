from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from utils.orm import update_by_batches
from web.apps.payments.models import (
    Payment,
    PaymentStatus,
    MerchantType,
)


@shared_task
def set_expired_payments(
        batch_size: int = 500,
) -> int:
    return update_by_batches(
        manager=Payment.objects,
        filters=dict(
            status=PaymentStatus.PENDING,
            expires_at__lte=timezone.now(),
        ),
        update_kwargs=dict(status=PaymentStatus.EXPIRED),
        batch_size=batch_size,
    )