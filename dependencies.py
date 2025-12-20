from typing import Annotated

from aiogram import Bot, Dispatcher
from fastapi import Depends
from fastapi.requests import Request


def get_bot(request: Request) -> Bot:
    return request.app.state.bot


CurrentBot = Annotated[Bot, Depends(get_bot)]


def get_dp(request: Request) -> Dispatcher:
    return request.app.state.dp


CurrentDispatcher = Annotated[Dispatcher, Depends(get_dp)]
