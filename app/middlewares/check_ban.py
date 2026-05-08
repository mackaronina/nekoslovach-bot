import logging
from typing import Awaitable, Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.utils.dao import UserDAO


class CheckBanMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: dict[str, Any]) -> Any:
        user = data['event_from_user']
        if await UserDAO.is_banned(user.id):
            logging.info(f'Message from banned user with id {user.id}')
            return None
        return await handler(event, data)
