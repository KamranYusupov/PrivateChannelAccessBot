import pprint

import loguru
from aiogram.types import Invoice
from django.conf import settings
from django.db import transaction
from pydantic import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError

from common.exceptions import PaymentAlreadyProcessed
from services.business import payment
from services.business.payment import PaymentUseCase
from services.infra.choices.product_type import product_type_helper
from web.api.v1.payments.crypto_bot.schemas import UpdateWebhookSchema, InvoiceStatus
from web.apps.payments.models import Payment
from web.apps.telegram_users.models import TelegramUser
from web.apps.telegram_users.tasks import send_message_task
from web.apps.telegram_users.tasks.infra import delete_message_task


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def update_webhook(request: Request):
    try:
        schema = UpdateWebhookSchema.model_validate(request.data)
    except ValidationError as e:
        from pprint import pprint

        pprint(e.errors())

        raise DRFValidationError(e.errors())

    invoice = schema.payload

    telegram_user = (
        TelegramUser.objects
        .only('id')
        .filter(
            telegram_id=invoice.payload.telegram_id
        )
        .first()
    )
    if not telegram_user:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if invoice.status != InvoiceStatus.PAID:
        return Response(status=status.HTTP_200_OK)

    product_type = product_type_helper.get_choice_by_value(
        invoice.payload.product_type_value
    )
    if not product_type:
        return Response(
            data={'error': 'incorrect product_type'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            subscription, payment = PaymentUseCase.execute(
                telegram_user_id=telegram_user.id,
                payment_id=invoice.payload.payment_id,
                tariff_id=invoice.payload.tariff_id,
                merchant_payment_id=str(invoice.invoice_id),
                product_type=product_type,
                merchant_payload=request.data,
            )
            delete_message_task.delay(
                chat_id=invoice.payload.telegram_id,
                message_id=payment.invoice_message_id
            )
            channel_link_button = {
                'text': '🚀 Вступить в приватный канал',
                'url': settings.PRIVATE_CHANNEL_LINK,
            }
            inline_keyboard = [
                [channel_link_button],
            ]
            send_message_task.delay(
                chat_id=invoice.payload.telegram_id,
                text='🎉 Оплата прошла успешно!',
                reply_markup={'inline_keyboard': inline_keyboard},
            )
        return Response(status=status.HTTP_201_CREATED)
    except Payment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except PaymentAlreadyProcessed:
        return Response(status=status.HTTP_200_OK)
