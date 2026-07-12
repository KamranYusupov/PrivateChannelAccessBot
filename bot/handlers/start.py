import loguru
from aiogram import Router, types, F, html
from aiogram.filters import CommandStart, Command
from aiogram.types import LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.loader import bot
from web.core import settings
router = Router()


@router.message(CommandStart())
async def start_command_handler(
    message: types.Message,
):
    message_text = f'Привет, {message.from_user.first_name}.'
    await message.answer(message_text)

    amount = int(settings.SUBSCRIPTION_GLOBAL_AMOUNT) * 100
    await message.answer_invoice(
        title="Оплата доступа",
        description="Вход в закрытый канал",
        payload="test_invoice_payload",
        provider_token=settings.YKASSA_TOKEN,
        currency="RUB",
        test=True,
        prices=[LabeledPrice(label="Подписка на Стеллу", amount=amount)],
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(
    pre_checkout_query: types.PreCheckoutQuery,
):
    loguru.logger.info(payload)
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True,
    )


@router.message(F.successful_payment)
async def successful_payment(
    message: types.Message,
):
    payload = message.successful_payment.invoice_payload
    loguru.logger.info(payload)

    try:
        # 2. Генерируем ОДНОРАЗОВУЮ ссылку
        limited_link_obj = await bot.create_chat_invite_link(
            chat_id=settings.PRIVATE_CHANNEL_ID,
            member_limit=1,
        )

        # 3. Делаем красивую кнопку с этой ссылкой
        builder = InlineKeyboardBuilder()
        builder.button(
            text="🚀 Вступить в приватный канал",
            url=limited_link_obj.invite_link
        )

        # 4. Отправляем юзеру
        await message.answer(
            text="🎉 Оплата прошла успешно!\n\n"
                 "Вот твоя индивидуальная ссылка для входа. "
                 f"Она сработает <b>только один раз</b> так что никуда её не пересылай.",
            reply_markup=builder.as_markup()
        )

    except Exception as e:
        loguru.logger.error(f"Ошибка при выдаче ссылки юзеру: {e}")
        await message.answer(
            "Оплата прошла, но возникла ошибка с выдачей ссылки. "
            "Пожалуйста, напиши в поддержку!"
        )
    

