from typing import List

from aiogram import Dispatcher

from .users_handlers import user_router

def activate_user(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(user_router)

__all__: List[str] = [
    'activate_user'
]