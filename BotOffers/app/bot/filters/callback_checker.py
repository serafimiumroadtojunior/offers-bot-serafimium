from typing import Optional

from aiogram.filters import Filter
from aiogram.types import CallbackQuery

from app.bot.settings import Settings
from app.bot.keyboards import ButtonsCallbackInfos, SendUserCallback


class MyFilter(Filter):
    async def __call__(
    self, 
    query: CallbackQuery,
    settings: Settings
) -> bool:
        data: Optional[str] = query.data

        if not data:
            return False
        
        buttonsinfo: ButtonsCallbackInfos = ButtonsCallbackInfos.unpack(data)
        senduser: SendUserCallback = SendUserCallback.unpack(data)

        if buttonsinfo.admin_id != settings.admin_id:
            return False
        
        if senduser.admin_id != settings.admin_id:
            return False
        
        return True