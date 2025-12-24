from aiogram import Router, F
from aiogram.types import Message
from openai import AsyncOpenAI

from app.keyboards.posting import get_posting_keyboard
from app.middlewares.send_error import SendErrorMiddleware
from app.utils.ai_generate import generate_new_from_text, generate_poll, generate_new_from_img_and_caption, \
    generate_new_from_img

router = Router()
router.message.filter(F.chat.type == 'private')
router.message.middleware(SendErrorMiddleware())


@router.message(F.photo, F.caption)
async def msg_photo_and_caption(message: Message, ai_client: AsyncOpenAI) -> None:
    new_text = await generate_new_from_img_and_caption(ai_client, message)
    await message.answer_photo(message.photo[-1].file_id, caption=new_text, reply_markup=get_posting_keyboard())
    poll = await generate_poll(ai_client, new_text)
    await message.answer_poll(**poll, reply_markup=get_posting_keyboard())


@router.message(F.photo)
async def msg_photo(message: Message, ai_client: AsyncOpenAI) -> None:
    new_text = await generate_new_from_img(ai_client, message)
    await message.answer_photo(message.photo[-1].file_id, caption=new_text, reply_markup=get_posting_keyboard())
    poll = await generate_poll(ai_client, new_text)
    await message.answer_poll(**poll, reply_markup=get_posting_keyboard())


@router.message(F.text | F.caption)
async def msg_text(message: Message, ai_client: AsyncOpenAI) -> None:
    new_text = await generate_new_from_text(ai_client, message)
    await message.answer(new_text, reply_markup=get_posting_keyboard())
    poll = await generate_poll(ai_client, new_text)
    await message.answer_poll(**poll, reply_markup=get_posting_keyboard())
