from typing import List

from aiogram import Dispatcher

from .admin_handlers import admin_router

def activate_admin(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(admin_router)

__all__: List[str] = [
    'activate_admin'
]