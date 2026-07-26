from pydantic import BaseModel


class YKASSAInvoicePayloadSchema(BaseModel):
    payment_id: int
    tariff_id: int
    product_type_value: str

