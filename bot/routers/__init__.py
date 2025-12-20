from aiogram import Router

from bot.routers.start import router as start_router
from bot.routers.faq import router as faq_router
from bot.routers.transactions import router as transactions_router


def get_main_router() -> Router:
    main_router = Router()
    main_router.include_router(start_router)
    main_router.include_router(faq_router)
    main_router.include_router(transactions_router)
    return main_router
