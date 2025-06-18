from typing import List

from aiogram import Dispatcher

from .type_group_check import CheckGroupMiddleware


def setup_outer(dispatcher: Dispatcher) -> None:
    dispatcher.message.outer_middleware(CheckGroupMiddleware())

__all__: List[str] = [
    "setup_outer"
]