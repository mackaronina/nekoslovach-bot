import html
from typing import Awaitable, Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message


class SendErrorMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, dict[str, Any]], Awaitable[Any]], message: Message,
                       data: dict[str, Any]) -> Any:
        try:
            return await handler(message, data)
        except Exception as e:
            await message.reply(f'Произошла ошибка\n{html.escape(str(e)[:500])}')
            raise e
