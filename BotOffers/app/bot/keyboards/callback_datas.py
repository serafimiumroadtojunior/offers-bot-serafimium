from typing import Optional

from aiogram.filters.callback_data import CallbackData


class PayingCallback(CallbackData, prefix='paying'):
    action: str
    user_id: int
    stars_amount: int

class SendUserCallback(CallbackData, prefix='late_user'):
    admin_id: Optional[int] = None
    user_id: int
    full_name: str

class ButtonsCallbackInfos(CallbackData, prefix='buttons'):
    admin_id: Optional[int] = None
    action: str
    user_id: int

class LanguageCallback(CallbackData, prefix='language'):
    locale: str
    user_id: int