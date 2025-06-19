from typing import List

from redis.asyncio import Redis
from aiogram import Bot, Router
from aiogram_i18n import I18nContext
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.utils import answer_message
from app.bot.keyboards import LanguageCallback
from app.bot.database import get_user_locale, add_user_info

common_router: Router = Router()

@common_router.message(Command("locale"))
async def command_locale(
    message: Message,
    redis: Redis,
    i18n: I18nContext,
    bot: Bot
) -> None:
    user_id: int = message.chat.id
    locale: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )

    buttons_texts: List[str] = [
        'En🇬🇧',
        'Ru🇷🇺',
        'Ua🇺🇦'
    ]

    callback_datas: List[str] = [
            LanguageCallback(locale='en', user_id=user_id).pack(),
            LanguageCallback(locale='ru', user_id=user_id).pack(),
            LanguageCallback(locale='ua', user_id=user_id).pack()
        ]

    await answer_message(
        bot=bot,
        chat_id=user_id,
        buttons_level=2,
        button_texts=buttons_texts,
        callback_datas=callback_datas,
        text=i18n.get(
            "locale-chose",
            locale
        )
    )


@common_router.message(Command('help'))
async def command_help(
    message: Message,
    redis: Redis,
    i18n: I18nContext,
    bot: Bot
):
    user_id: int = message.chat.id
    locale: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )

    await answer_message(
        bot=bot,
        chat_id=user_id,
        text=i18n.get(
            'help-text',
            locale
        )
    )


@common_router.callback_query(LanguageCallback.filter())
async def callback_language(
    i18n: I18nContext,
    redis: Redis,
    callback_data: LanguageCallback,
    bot: Bot
) -> None:
    user_id: int = callback_data.user_id
    locale: str = callback_data.locale

    await add_user_info(
        user_locale=locale, 
        user_id=user_id
    )

    locale_text: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )

    await answer_message(
        bot=bot,
        user_id=user_id,
        text=i18n.get(
            "locale-changed",
            locale_text
        )
    )