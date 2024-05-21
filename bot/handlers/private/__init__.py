from aiogram import Router

from bot.handlers.private.admin_handler import admin_router
from bot.handlers.private.callback_handler import callback_router
from bot.handlers.private.main_handler import main_router
from bot.handlers.private.inline_handler import inline_router

private_handler_router = Router()

private_handler_router.include_routers(
    callback_router,
    admin_router,
    main_router,
    inline_router
)
