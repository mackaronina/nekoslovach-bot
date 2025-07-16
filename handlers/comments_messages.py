from aiogram import Router, F
from aiogram.types import Message
from openai import AsyncOpenAI

from config import settings
from middlewares.comments import CommentsMiddleware
from utils.ai_generate import generate_reply_comment_img_and_caption, generate_reply_comment_img, \
    generate_reply_comment_text

router = Router()
router.message.filter(F.chat.id == settings.comments_chat_id, F.reply_to_message)
router.message.middleware(CommentsMiddleware())


@router.message(F.photo, F.caption)
async def msg_photo_and_caption(message: Message, ai_client: AsyncOpenAI, post_text: str) -> int:
    reply_text = await generate_reply_comment_img_and_caption(ai_client, message, post_text)
    reply = await message.reply(reply_text)
    return reply.message_id


@router.message(F.photo | (F.sticker & ~F.sticker.is_animated & ~F.sticker.is_video))
async def msg_photo(message: Message, ai_client: AsyncOpenAI, post_text: str) -> int:
    reply_text = await generate_reply_comment_img(ai_client, message, post_text)
    reply = await message.reply(reply_text)
    return reply.message_id


@router.message(F.text | F.caption)
async def msg_text(message: Message, ai_client: AsyncOpenAI, post_text: str) -> int:
    reply_text = await generate_reply_comment_text(ai_client, message, post_text)
    reply = await message.reply(reply_text)
    return reply.message_id
