from aiogram.filters.callback_data import CallbackData


class PayingCallback(CallbackData, prefix='paying'):
    action: str
    user_id: int
    stars_amount: int

class SendUserCallback(CallbackData, prefix='late_user'):
    user_id: int
    full_name: str

class ButtonsCallbackInfos(CallbackData, prefix='buttons'):
    action: str
    user_id: int

class LanguageCallback(CallbackData, prefix='language'):
    locale: str
    user_id: int