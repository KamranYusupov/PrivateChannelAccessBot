from datetime import timedelta
from typing import Tuple, Union, Optional, Dict, Any

from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils import timezone

from common.exceptions import PaymentAlreadyProcessed
from common.typing import ModelT
from web.apps.consultations.models import Consultation
from web.apps.face_rates.models import FaceRate
from web.apps.payments.models import PaymentStatus, Payment, ProductType
from web.apps.subscriptions.models import Subscription, PrivateChannelTariff
from web.apps.telegram_users.models import TelegramUser

Product = Union[
    Subscription,
    Consultation,
    FaceRate,
]

class PaymentUseCase:

    @classmethod
    def execute(
            cls,
            *,
            telegram_user_id: int,
            payment_id: int,
            tariff_id: int,
            merchant_payment_id: str,
            product_type: ProductType,
            merchant_payload: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Product, Payment]:
        process_payment_method_kwargs = dict(
            telegram_user_id=telegram_user_id,
            payment_id=payment_id,
            tariff_id=tariff_id,
            merchant_payment_id=merchant_payment_id,
            merchant_payload=merchant_payload
        )
        match product_type:
            case ProductType.PRIVATE_CHANNEL_ACCESS:
                return cls._process_subscription_payment(
                    **process_payment_method_kwargs
                )
            case _:
                raise ValueError(
                    f'Product type: "{product_type.label}" not supported yet.',
                )

    @classmethod
    @sync_to_async
    def aexecute(
            cls,
            *,
            telegram_user_id: int,
            payment_id: int,
            tariff_id: int,
            merchant_payment_id: str,
            product_type: ProductType,
            merchant_payload: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Product, Payment]:
        return cls.execute(
            telegram_user_id=telegram_user_id,
            payment_id=payment_id,
            tariff_id=tariff_id,
            merchant_payment_id=merchant_payment_id,
            product_type=product_type,
            merchant_payload=merchant_payload
        )

    @classmethod
    def _process_subscription_payment(
            cls,
            *,
            telegram_user_id: int,
            payment_id: int,
            tariff_id: int,
            merchant_payment_id: str,
            merchant_payload: Optional[Dict[str, Any]] = None,
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
            payment.merchant_payload = merchant_payload
            payment.save(
                update_fields=[
                    'status',
                    'merchant_payment_id',
                    'merchant_payload',
                ]
            )
            TelegramUser.objects.filter(
                id=telegram_user_id,
                has_channel_access=False
            ).update(has_channel_access=True)

        return subscription, payment
