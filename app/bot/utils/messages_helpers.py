import asyncio
from contextlib import suppress
from typing import Optional, Sequence

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from app.bot.keyboards import customed_keyboard


async def answer_message(
    bot: Bot,
    chat_id: int,
    text: str,
    delay: int = 30,
    flag: bool = False,
    button_texts: Optional[Sequence[str]] = None,
    callback_datas: Optional[Sequence[str]] = None,
    buttons_level: Optional[int] = None
) -> Message:
    response_message: Message = await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=await customed_keyboard(
            buttons_text=button_texts,
            callback_data=callback_datas,
            buttons_level=buttons_level
        )
    )

    if flag:
        asyncio.create_task(
            delayed_delete(
                message=response_message,
                delay=delay
            )
        )

        return response_message
    return response_message


async def delayed_delete(
    delay: int, 
    message: Message
) -> None:
    with suppress(TelegramBadRequest, AttributeError):
        await asyncio.sleep(delay)
        await message.delete()