from aiogram import Router

from bot.handlers.start import router as start_router
from bot.handlers.product_type import router as product_type_router
from bot.handlers.tariffs import router as tariffs_type_router
from bot.handlers.payment import router as payment_type_router

def get_main_router():
    main_router = Router()

    main_router.include_router(start_router)
    main_router.include_router(product_type_router)
    main_router.include_router(tariffs_type_router)
    main_router.include_router(payment_type_router)

    return main_router