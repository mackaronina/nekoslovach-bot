from typing import Callable, Dict, Any, Awaitable, Optional

from aiogram import BaseMiddleware
from aiogram.types import Message

from config import TG_ANONYMOUS_ID


class CommentsMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], message: Message,
                       data: Dict[str, Any]) -> Optional[int]:
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


def post_to_text(message: Message) -> str:
    if message.poll is not None:
        return f'Опрос. {message.poll.question}\n1. {message.poll.options[0].text}\n2. {message.poll.options[1].text}'
    return message.text or message.caption
