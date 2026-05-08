from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from app.config import TG_ANONYMOUS_ID
from app.utils.text import post_to_text


class CommentsMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, dict[str, Any]], Awaitable[Any]], message: Message,
                       data: dict[str, Any]) -> int | None:
        comment_ids = data['comment_ids']
        post_texts = data['post_texts']
        if message.reply_to_message.from_user.id == TG_ANONYMOUS_ID:
            post_id = message.reply_to_message.message_id
            post_texts[post_id] = post_to_text(message.reply_to_message)
        else:
            post_id = next(
                (post for post, comments in comment_ids.items() if message.reply_to_message.message_id in comments),
                None
            )
            if post_id is None or post_id not in post_texts:
                return None
        if post_id in comment_ids:
            comment_ids[post_id].append(message.message_id)
        else:
            comment_ids[post_id] = [message.message_id]
        data['post_text'] = post_texts[post_id]
        reply_id = await handler(message, data)
        comment_ids[post_id].append(reply_id)
        return reply_id
