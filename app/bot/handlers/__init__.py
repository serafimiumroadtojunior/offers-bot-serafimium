from typing import List

from aiogram import Dispatcher

from .admin import activate_admin
from .common import activate_common
from .user import activate_user

def setup_routers(dispatcher: Dispatcher) -> None:
    activate_admin(dispatcher=dispatcher)
    activate_common(dispatcher=dispatcher)
    activate_user(dispatcher=dispatcher)

__all__: List[str] = [
    'setup_routers'
]