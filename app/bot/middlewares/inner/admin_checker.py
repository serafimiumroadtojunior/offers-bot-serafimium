from typing import Any, Awaitable, Callable, Dict, Optional

from redis.asyncio import Redis
from aiogram_i18n import I18nContext
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, TelegramObject

from app.bot.settings import Settings
from app.bot.utils import answer_message
from app.bot.database import get_user_locale


class AdminCheckerMiddleware(BaseMiddleware):
    def __init__(
        self, 
        bot: Bot, 
        redis: Redis,
        settings: Settings
    ):
        self.bot: Bot = bot
        self.redis: Redis = redis
        self.settings: Settings = settings

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            if event.from_user is not None:
                user_id: int = event.from_user.id
                i18n: Optional[I18nContext] = data.get('i18n')
                locale: str = await get_user_locale(
                    user_id=user_id,
                    redis=self.redis
                )

                if not i18n:
                    return await handler(event, data)
                
                if user_id != self.settings.admin_id:
                    return await answer_message(
                            bot=self.bot,
                            chat_id=user_id,
                            text=i18n.get(
                                'error-admins',
                                locale
                            )
                        )

                return await handler(event, data)
        return await handler(event, data)
