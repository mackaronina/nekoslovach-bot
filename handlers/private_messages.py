from aiogram import Router, F
from aiogram.types import Message
from openai import AsyncOpenAI

from keyboards.kb_post_to_channel import build_keyboard
from utils.ai_generate import generate_new_from_text, generate_poll, generate_new_from_img_and_caption, \
    generate_new_from_img

router = Router()
router.message.filter(F.chat.type == 'private')


@router.message(F.photo, F.caption)
async def msg_photo_and_caption(message: Message, ai_client: AsyncOpenAI) -> None:
    try:
        new_text = await generate_new_from_img_and_caption(ai_client, message)
        await message.answer_photo(message.photo[-1].file_id, caption=new_text, reply_markup=build_keyboard())
        poll = await generate_poll(ai_client, new_text)
        await message.answer_poll(**poll, reply_markup=build_keyboard())
    except Exception as e:
        await message.reply(str(e))


@router.message(F.photo)
async def msg_photo(message: Message, ai_client: AsyncOpenAI) -> None:
    try:
        new_text = await generate_new_from_img(ai_client, message)
        await message.answer_photo(message.photo[-1].file_id, caption=new_text, reply_markup=build_keyboard())
        poll = await generate_poll(ai_client, new_text)
        await message.answer_poll(**poll, reply_markup=build_keyboard())
    except Exception as e:
        await message.reply(str(e))


@router.message(F.text | F.caption)
async def msg_text(message: Message, ai_client: AsyncOpenAI) -> None:
    try:
        new_text = await generate_new_from_text(ai_client, message)
        await message.answer(new_text, reply_markup=build_keyboard())
        poll = await generate_poll(ai_client, new_text)
        await message.answer_poll(**poll, reply_markup=build_keyboard())
    except Exception as e:
        await message.reply(str(e))
