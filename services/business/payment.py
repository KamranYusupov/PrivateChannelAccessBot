from datetime import timedelta
from typing import Tuple

from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils import timezone

from common.exceptions import PaymentAlreadyProcessed
from common.typing import ModelT
from web.apps.payments.models import PaymentStatus, Payment, ProductType
from web.apps.subscriptions.models import Subscription, PrivateChannelTariff


class PaymentUseCase:

    @staticmethod
    @sync_to_async
    def process_subscription_payment(
            *,
            telegram_user_id: int,
            payment_id: int,
            tariff_id: int,
            merchant_payment_id: str,
    ) -> Tuple[Subscription, Payment]:
        term_days = (
            PrivateChannelTariff.objects
            .get_term_days_by_id(tariff_id)
        )
        subscription_expires_at = timezone.now() + timedelta(days=term_days)
        with transaction.atomic():
            payment = (
                Payment.objects
                .select_for_update()
                .get(id=payment_id)
            )
            if payment.status == PaymentStatus.SUCCESS:
                raise PaymentAlreadyProcessed

            subscription = Subscription.objects.create(
                telegram_user_id=telegram_user_id,
                payment_id=payment.id,
                tariff_id=tariff_id,
                expires_at=subscription_expires_at,
            )
            payment.status = PaymentStatus.SUCCESS
            payment.merchant_payment_id = merchant_payment_id
            payment.save(
                update_fields=[
                    'status',
                    'merchant_payment_id',
                ]
            )

        return subscription, payment
