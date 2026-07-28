import json

from bot.schemas.payment import InvoicePayloadSchema


class PayloadService:

    @staticmethod
    def get_invoice_payload_schema(
            invoice_payload: str
    ) -> InvoicePayloadSchema:
        invoice_payload_dict = json.loads(invoice_payload)

        return InvoicePayloadSchema(
            payment_id=invoice_payload_dict['payment_id'],
            tariff_id=invoice_payload_dict['tariff_id'],
            product_type_value=invoice_payload_dict['product_type_value'],
            telegram_id=invoice_payload_dict['telegram_id'],
        )
