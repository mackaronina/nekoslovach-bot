from aiogram import Router, F
from aiogram.types import Message
from openai import AsyncOpenAI

from config import COMMENTS_CHATID, TELEGRAM_ANONYMOUS_ID
from utils.ai_generate import generate_reply_to_comment_new, generate_reply_to_comment_poll

router = Router()
# Message in comments chat and replying to channel message
router.message.filter(F.chat.id == COMMENTS_CHATID, F.reply_to_message.from_user.id == TELEGRAM_ANONYMOUS_ID)


@router.message(F.text | F.caption, F.reply_to_message.text | F.reply_to_message.caption)
async def msg_reply_comment_new(message: Message, ai_client: AsyncOpenAI) -> None:
    reply_text = await generate_reply_to_comment_new(ai_client, message)
    await message.reply(reply_text)


@router.message(F.text | F.caption, F.reply_to_message.poll)
async def msg_reply_comment_poll(message: Message, ai_client: AsyncOpenAI) -> None:
    reply_text = await generate_reply_to_comment_poll(ai_client, message)
    await message.reply(reply_text)
