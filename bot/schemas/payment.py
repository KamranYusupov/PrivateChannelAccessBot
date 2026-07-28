from pydantic import BaseModel


class InvoicePayloadSchema(BaseModel):
    payment_id: int
    tariff_id: int
    product_type_value: str
    telegram_id: int


