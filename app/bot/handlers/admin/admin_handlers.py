from typing import Dict, Any, Optional

from redis.asyncio import Redis
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    CallbackQuery, Message, 
    User, InaccessibleMessage
)

from app.bot.settings import Settings
from app.bot.utils import answer_message, parse_admin_send
from app.bot.states import StateSend
from app.bot.keyboards import SendUserCallback, ButtonsCallbackInfos
from app.bot.database import (
    add_user_info, get_user_locale,
    get_late_user, get_user_check
)

admin_router: Router = Router()

@admin_router.message(Command("adminsend"))
async def command_admin_send(
    message: Message,
    redis: Redis,
    settings: Settings,
    i18n: I18nContext,
    command: CommandObject,
    bot: Bot
) -> None:
    admin_locale: str = await get_user_locale(
        user_id=settings.admin_id,
        redis=redis
    )

    if not command.args:
        return await answer_message(
            bot=bot,
            chat_id=settings.admin_id,
            text=i18n.get(
                "error-args", 
                admin_locale
            )
        )

    user_id, send_text = parse_admin_send(args=command.args)

    if not user_id or not send_text:
        return await answer_message(
            bot=bot,
            chat_id=settings.admin_id,
            text=i18n.get(
                "error-args", 
                admin_locale
            )
        )
    
    user_locale: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )

    return await answer_message(
        bot=bot,
        buttons_level=1,
        chat_id=user_id,
        text=i18n.get(
            "admin-send-user",
            user_locale,
            send_text=send_text
        ),
        button_texts=[
            i18n.get(
                "answer-button", 
                user_locale
            )
        ],
        callback_datas=[
            ButtonsCallbackInfos(
                action="user_send",
                user_id=user_id
            ).pack()
        ]
    )


@admin_router.message(Command("late_users"))
async def command_late_users(
    message: Message,
    redis: Redis,
    i18n: I18nContext,
    bot: Bot
) -> None:
    if not isinstance(message.from_user, User):
        return None

    user_id: int = message.chat.id
    late_buttons, late_callbacks = await get_late_user()
    locale: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )

    if not late_buttons or not late_callbacks:
        return await answer_message(
            bot=bot,
            chat_id=user_id,
            text=i18n.get(
                "error-late-users", 
                locale
            )
        )

    return await answer_message(
        bot=bot,
        chat_id=user_id,
        button_texts=late_buttons,
        button_callbacks=late_callbacks,
        buttons_level=2,
        text=i18n.get(
            "something-users", 
            locale
        )
    )


@admin_router.message(Command("check_checker"))
async def command_check_checker(
    message: Message,
    redis: Redis,
    command: CommandObject,
    i18n: I18nContext,
    bot: Bot   
) -> None:
    user_id: int = message.chat.id
    locale: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )  

    if not command.args:
        return await answer_message(
            bot=bot,
            chat_id=user_id,
            text=i18n.get(
                "error-args", 
                locale
            )
        )

    charge_id, amount, status, code = await get_user_check(
        check_id=command.args, 
        locale=locale, 
        i18n=i18n
    )

    if not charge_id or not code:
        return await answer_message(
            bot=bot,
            chat_id=user_id,
            text=i18n.get(
                "error-check", 
                locale
            )
        )
    
    if not amount or not status:
        return await answer_message(
            bot=bot,
            chat_id=user_id,
            text=i18n.get(
                "error-check", 
                locale
            )
        )

    return await answer_message(
        bot=bot,
        chat_id=user_id,
        text=i18n.get(
            "check-info",
            locale,
            code=code,
            stars_amount=amount,
            status=status,
            charge_id=charge_id
        )
    )


@admin_router.callback_query(SendUserCallback.filter())
async def callback_late_user(
    callback: CallbackQuery,
    redis: Redis,
    fsm: FSMContext,
    i18n: I18nContext,
    callback_data: SendUserCallback,
    bot: Bot
) -> None:
    if isinstance(callback.message, InaccessibleMessage):
        return None
    
    if not callback.message:
        return None

    message: Message = callback.message
    chat_id: int = message.chat.id
    user_id: int = callback_data.user_id
    full_name: str = callback_data.full_name
    locale: str = await get_user_locale(
        user_id=chat_id,
        redis=redis
    )

    await fsm.update_data(
        data={
            "user_id": user_id,
            "full_name": full_name
        }
    )

    await fsm.set_state(StateSend.text_send)
    await answer_message(
        bot=bot,
        chat_id=chat_id,
        text=i18n.get(
            "fsm-send",
            locale
        )
    )


@admin_router.callback_query(ButtonsCallbackInfos.filter(F.action == "ban"))
async def callback_ban_user(
    callback: CallbackQuery,
    redis: Redis,
    settings: Settings,
    i18n: I18nContext,
    callback_data: ButtonsCallbackInfos,
    bot: Bot
) -> None:
    if isinstance(callback.message, InaccessibleMessage):
        return None
    
    if not callback.message:
        return None

    admin_id: int = settings.admin_id
    user_id: int = callback_data.user_id
    admin_locale: str = await get_user_locale(
        user_id=admin_id,
        redis=redis
    )
    user_locale: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )

    await add_user_info(
        user_id=user_id,
        status="Banned"
    )
    
    await answer_message(
        bot=bot,
        user_id=admin_id,
        text=i18n.get(
            "successful-block",
            admin_locale
        )
    )

    await answer_message(
        bot=bot,
        user_id=user_id,
        text=i18n.get(
            "user-banned",
            user_locale
        )
    )


@admin_router.callback_query(ButtonsCallbackInfos.filter(F.action == "unban"))
async def callback_unban_user(
    callback: CallbackQuery,
    settings: Settings,
    redis: Redis,
    i18n: I18nContext,
    callback_data: ButtonsCallbackInfos,
    bot: Bot
) -> None:
    if isinstance(callback.message, InaccessibleMessage):
        return None
    
    if not callback.message:
        return None

    admin_id: int = settings.admin_id
    user_id: int = callback_data.user_id
    admin_locale: str = await get_user_locale(
        user_id=admin_id,
        redis=redis
    )
    user_locale: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )

    await add_user_info(
        user_id=user_id,
        status="Unbanned"
    )
    
    await answer_message(
        bot=bot,
        user_id=admin_id,
        text=i18n.get(
            "successful-unblock",
            admin_locale
        )
    )

    await answer_message(
        bot=bot,
        user_id=user_id,
        text=i18n.get(
            "user-unbanned",
            user_locale
        )
    )


@admin_router.message(StateSend.text_send)
async def message_send_text(
    message: Message,
    redis: Redis,
    fsm: FSMContext,
    settings: Settings,
    i18n: I18nContext,
    bot: Bot
) -> None:
    if not isinstance(message.from_user, User):
        return None
    
    if not message.text:
        return None

    data: Dict[str, Any] = await fsm.get_data()    
    admin_id: int = settings.admin_id
    user_id: Optional[int] = data.get("user_id")
    full_name: Optional[str] = data.get("full_name")
    user_locale: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )
    admin_locale: str = await get_user_locale(
        user_id=admin_id,
        redis=redis
    )

    if not user_id or not full_name:
        return await answer_message(
            bot=bot,
            chat_id=admin_id,
            text=i18n.get(
                "error-fsm-data", 
                admin_locale
            )
        )

    await answer_message(
        bot=bot,
        user_id=user_id,
        text=message.text,
        buttons_level=1,
        button_texts=[
            i18n.get(
                'answer-button',
                user_locale
            )
        ],
        callback_datas=[
            ButtonsCallbackInfos(
                action="user_send",
                user_id=admin_id
            ).pack()
        ]
    )

    await answer_message(
        bot=bot,
        chat_id=admin_id,
        text=i18n.get(
            "fsm-send",
            admin_locale
        )
    )

    await fsm.clear() 