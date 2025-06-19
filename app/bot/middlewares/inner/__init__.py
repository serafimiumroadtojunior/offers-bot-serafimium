from typing import List

from aiogram import Dispatcher, Bot
from redis.asyncio import Redis

from app.bot.settings import Settings
from .admin_checker import AdminCheckerMiddleware
from .anti_flood import AntiFloodMiddleware


def setup_inner(
    dispatcher: Dispatcher,
    settings: Settings,
    redis: Redis,
    bot: Bot
) -> None:
    dispatcher.message.middleware(AntiFloodMiddleware())
    dispatcher.callback_query.middleware(AntiFloodMiddleware())
    dispatcher.message.middleware(
        AdminCheckerMiddleware(
            settings=settings,
            redis=redis,
            bot=bot
        )
    )

__all__: List[str] = [
    "AdminCheckerMiddleware",
    'AntiFloodMiddleware'
]