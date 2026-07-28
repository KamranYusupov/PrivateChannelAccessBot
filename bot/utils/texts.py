from datetime import datetime, timedelta
from decimal import Decimal

from aiogram import html


tariff_text_template = (
    '<b>{title}</b>\n\n'
    '{description}\n\n'
    'Стоимость: <b>{price} ₽</b>\n\n'
)
def get_product_text(
        title: str,
        description: str,
        price: int | Decimal,
) -> str:
    return tariff_text_template.format(
        title=title,
        description=description,
        price=price,
    )


subscription_info_text_template = (
    '📱 Подписка действительна до <b>{expires_at}</b> '
    'включительно ({expires_in_days} дней).'
)
def get_subscription_info_text(
        expires_in_days: int,
        now: datetime = datetime.now(),
):
    expires_at = now + timedelta(days=expires_in_days)
    expires_at_str = expires_at.strftime('%d.%m.%Y')
    return subscription_info_text_template.format(
        expires_at=expires_at_str,
        expires_in_days=expires_in_days,
    )