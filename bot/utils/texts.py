from decimal import Decimal

from aiogram import html


face_rate_tariff_text_template = (
    '<b>{title}</b>\n\n'
    '{description}\n\n'
    'Стоимость: <b>{price} ₽</b>\n\n'
)
def get_product_text(
        title: str,
        description: str,
        price: int | Decimal,
) -> str:
    return face_rate_tariff_text_template.format(
        title=title,
        description=description,
        price=price,
    )