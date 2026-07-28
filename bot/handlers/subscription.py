from aiogram import Router, types, F
from django.utils import timezone

from bot.keyboards.inline import get_inline_keyboard
from bot.utils.texts import get_subscription_info_text
from web.apps.payments.models import ProductType
from web.apps.subscriptions.models import Subscription
from web.apps.telegram_users.models import TelegramUser
from web.db.orm_utils import aget_or_none

router = Router()

@router.message(F.text.lower() == '📱 моя подписка')
async def my_subscription_handler(
    message: types.Message,
):
    current_user = await aget_or_none(
        TelegramUser.objects.all(),
        telegram_id=message.from_user.id
    )

    if not current_user:
        return

    expires_in_days = await Subscription.objects.aget_expires_in_days(
        telegram_user_id=current_user.id,
    )

    reply_markup = get_inline_keyboard(
        buttons={
            '💰 Посмотреть тарифы': \
                ProductType.PRIVATE_CHANNEL_ACCESS.label
        }
    )

    if not expires_in_days:
        await message.answer(
            '📱 У вас нет активной подписки.\n\n'
            '💡 Оформите подписку, чтобы получить доступ к премиум функциям!',
            reply_markup=reply_markup
        )
        return

    message_text = get_subscription_info_text(
        now=timezone.now(),
        expires_in_days=expires_in_days,
    )
    await message.answer(
        message_text,
        reply_markup=reply_markup
    )