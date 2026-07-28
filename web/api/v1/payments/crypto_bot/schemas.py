from decimal import Decimal
from typing import Any, Annotated
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, field_validator, Field

from bot.schemas.payment import InvoicePayloadSchema

MoneyDecimal = Annotated[
    Decimal,
    Field(max_digits=20, decimal_places=8),
]

class InvoiceStatus(StrEnum):
    PAID = 'paid'
    ACTIVE = 'active'
    EXPIRED = 'expired'

class CryptoInvoiceSchema(BaseModel):
    invoice_id: int
    hash: str

    currency_type: str

    asset: str | None = None
    fiat: str | None = None

    amount: MoneyDecimal

    paid_asset: str
    paid_amount: MoneyDecimal

    description: str | None = None

    status: InvoiceStatus

    created_at: datetime
    paid_at: datetime | None = None

    paid_usd_rate: MoneyDecimal
    usd_rate: MoneyDecimal

    payload: InvoicePayloadSchema | None = None

    @field_validator('payload', mode='before')
    @classmethod
    def validate_payload(cls, value: Any) -> InvoicePayloadSchema:
        if isinstance(value, str):
            return InvoicePayloadSchema.model_validate_json(value)
        if isinstance(value, InvoicePayloadSchema):
            return value

        return InvoicePayloadSchema.model_validate(value)


class UpdateWebhookSchema(BaseModel):
    update_id: int
    update_type: str
    request_date: datetime

    payload: CryptoInvoiceSchema




