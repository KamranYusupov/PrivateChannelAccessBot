from decimal import Decimal
from typing import Any, Annotated
from datetime import datetime
from enum import StrEnum

from pydantic import field_validator, Field
from drf_pydantic import BaseModel

from bot.schemas.payment import InvoicePayloadSchema

MoneyDecimal = Annotated[
    Decimal,
    Field(max_digits=20, decimal_places=8),
]

class InvoiceStatus(StrEnum):
    PAID = 'paid'
    ACTIVE = 'active'
    EXPIRED = 'expired'

class CryptoBotInvoicePayloadSchema(BaseModel, InvoicePayloadSchema):
    telegram_id: int

    drf_config = {'validate_pydantic': True,}


class CryptoInvoiceSchema(BaseModel):
    invoice_id: int
    hash: str

    currency_type: str
    asset: str

    amount: MoneyDecimal
    paid_asset: str
    paid_amount: MoneyDecimal

    description: str
    status: InvoiceStatus

    created_at: datetime
    paid_at: datetime

    paid_usd_rate: MoneyDecimal
    usd_rate: MoneyDecimal

    payload: CryptoBotInvoicePayloadSchema

    @field_validator('payload', mode='before')
    @classmethod
    def ensure_list(cls, value: Any) -> InvoicePayloadSchema:
        if isinstance(value, str):
            return CryptoBotInvoicePayloadSchema.model_validate_json(value)
        return CryptoBotInvoicePayloadSchema.model_validate(value)

    drf_config = {'validate_pydantic': True,}


class UpdateWebhookSchema(BaseModel):
    update_id: int
    update_type: str
    request_date: datetime

    payload: CryptoInvoiceSchema

    drf_config = {'validate_pydantic': True,}




