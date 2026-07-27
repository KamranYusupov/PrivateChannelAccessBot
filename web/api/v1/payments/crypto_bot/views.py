from aiogram.types import Invoice
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from common.exceptions import PaymentAlreadyProcessed
from services.business.payment import PaymentUseCase
from services.infra.product_type import ProductTypeService
from web.api.v1.payments.crypto_bot.schemas import UpdateWebhookSchema, InvoiceStatus
from web.apps.payments.models import Payment, PaymentStatus, MerchantType
from web.apps.telegram_users.models import TelegramUser
from web.db.orm_utils import aget_or_none


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def update_webhook(request: Request):
    serializer = UpdateWebhookSchema.drf_serializer(
        data=request.data
    )
    serializer.is_valid(raise_exception=True)

    schema: UpdateWebhookSchema = UpdateWebhookSchema(**serializer.data)
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

    product_type = ProductTypeService.get_product_type_by_value(
        invoice.payload.product_type_value
    )
    if not product_type:
        return Response(
            data={'error': 'incorrect product_type'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        PaymentUseCase.execute(
            telegram_user_id=telegram_user.id,
            payment_id=invoice.payload.payment_id,
            tariff_id=invoice.payload.tariff_id,
            merchant_payment_id=str(invoice.invoice_id),
            product_type=product_type,
        )
        return Response(status=status.HTTP_201_CREATED)
    except Payment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except PaymentAlreadyProcessed:
        return Response(status=status.HTTP_200_OK)

