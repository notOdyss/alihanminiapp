from aiogram import Router

from logbot.routers.admin import router as admin_router


def get_logbot_router() -> Router:
    main_router = Router()
    main_router.include_router(admin_router)
    return main_router
