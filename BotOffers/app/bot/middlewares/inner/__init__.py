from typing import List

from aiogram import Dispatcher, Bot
from redis.asyncio.client import Redis

from app.bot.handlers.admin import admin_router
from app.bot.settings import Settings
from .admin_checker import AdminCheckerMiddleware, CallbackAdminCheckerMiddleware
from .anti_flood import AntiFloodMiddleware


def setup_inner(
    dispatcher: Dispatcher,
    settings: Settings,
    redis: Redis,
    bot: Bot
) -> None:
    dispatcher.message.middleware(AntiFloodMiddleware())
    dispatcher.callback_query.middleware(AntiFloodMiddleware())
    admin_router.message.middleware(
        AdminCheckerMiddleware(
            settings=settings,
            redis=redis,
            bot=bot
        )
    )
    admin_router.callback_query.middleware(
        CallbackAdminCheckerMiddleware(
            settings=settings,
            redis=redis
        )
    )

__all__: List[str] = [
    "AdminCheckerMiddleware",
    'AntiFloodMiddleware'
]