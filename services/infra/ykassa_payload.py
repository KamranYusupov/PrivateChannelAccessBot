import json

from bot.schemas.payment import YKASSAInvoicePayloadSchema


class YKASSAPayloadService:

    @staticmethod
    def get_invoice_payload_schema(
            invoice_payload: str
    ) -> YKASSAInvoicePayloadSchema:
        invoice_payload_dict = json.loads(invoice_payload)

        return YKASSAInvoicePayloadSchema(
            payment_id=invoice_payload_dict['payment_id'],
            tariff_id=invoice_payload_dict['tariff_id'],
            product_type_value=invoice_payload_dict['product_type_value'],
        )
