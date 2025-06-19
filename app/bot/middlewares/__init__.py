from typing import List

from aiogram import Dispatcher, Bot
from redis.asyncio import Redis
from app.bot.settings import Settings

from .inner import setup_inner
from .outer import setup_outer


def setup_middlewares(
    dispatcher: Dispatcher,
    settings: Settings,
    bot: Bot,
    redis: Redis
) -> None:
    setup_outer(dispatcher=dispatcher)
    setup_inner(
        dispatcher=dispatcher,
        settings=settings,
        redis=redis,
        bot=bot
    )

__all__: List[str] = [
    "setup_middlewares"
]