from aiogram import Router, F
from aiogram.types import Message
from openai import AsyncOpenAI

from config import COMMENTS_CHATID, TG_ANONYMOUS_ID, BOT_USERID
from utils.ai_generate import generate_reply_to_comment_new, generate_reply_to_comment_poll, \
    generate_reply_to_comment_dialog

router = Router()
router.message.filter(F.chat.id == COMMENTS_CHATID, F.text | F.caption)


@router.message(F.reply_to_message.from_user.id == TG_ANONYMOUS_ID,
                F.reply_to_message.text | F.reply_to_message.caption)
async def msg_reply_comment_new(message: Message, ai_client: AsyncOpenAI) -> None:
    reply_text = await generate_reply_to_comment_new(ai_client, message)
    await message.reply(reply_text)


@router.message(F.reply_to_message.from_user.id == TG_ANONYMOUS_ID, F.reply_to_message.poll)
async def msg_reply_comment_poll(message: Message, ai_client: AsyncOpenAI) -> None:
    reply_text = await generate_reply_to_comment_poll(ai_client, message)
    await message.reply(reply_text)


@router.message(F.reply_to_message.from_user.id == BOT_USERID, F.reply_to_message.text | F.reply_to_message.caption)
async def msg_reply_comment_dialog(message: Message, ai_client: AsyncOpenAI) -> None:
    reply_text = await generate_reply_to_comment_dialog(ai_client, message)
    await message.reply(reply_text)
