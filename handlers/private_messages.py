from aiogram import Router, F, Bot
from aiogram.types import Message, InputPollOption
from openai import AsyncOpenAI

from keyboards.kb_post_to_channel import build_keyboard
from utils.ai_generate import generate_new_from_text, news_text, generate_poll, generate_new_from_img_and_caption, \
    generate_new_from_img

router = Router()
router.message.filter(F.chat.type == 'private')


@router.message(F.photo, F.caption)
async def msg_photo_and_caption(message: Message, bot: Bot, ai_client: AsyncOpenAI) -> None:
    try:
        new = await generate_new_from_img_and_caption(bot, ai_client, message.photo[-1].file_id, message.caption)
        await message.answer_photo(message.photo[-1].file_id, caption=news_text(new, 'предложка'),
                                   reply_markup=build_keyboard())
        poll = await generate_poll(ai_client, new)
        await message.answer_poll(
            poll.question,
            [InputPollOption(text=poll.options[0][:100]), InputPollOption(text=poll.options[1][:100])],
            is_anonymous=True,
            reply_markup=build_keyboard()
        )
    except Exception as e:
        await message.reply(str(e))


@router.message(F.photo)
async def msg_photo(message: Message, bot: Bot, ai_client: AsyncOpenAI) -> None:
    try:
        new = await generate_new_from_img(bot, ai_client, message.photo[-1].file_id)
        await message.answer_photo(message.photo[-1].file_id, caption=news_text(new, 'предложка'),
                                   reply_markup=build_keyboard())
        poll = await generate_poll(ai_client, new)
        await message.answer_poll(
            poll.question,
            [InputPollOption(text=poll.options[0][:100]), InputPollOption(text=poll.options[1][:100])],
            is_anonymous=True,
            reply_markup=build_keyboard()
        )
    except Exception as e:
        await message.reply(str(e))


@router.message(F.text)
async def msg_text(message: Message, ai_client: AsyncOpenAI) -> None:
    try:
        new = await generate_new_from_text(ai_client, message.text)
        await message.answer(news_text(new, 'предложка'), reply_markup=build_keyboard())
        poll = await generate_poll(ai_client, new)
        await message.answer_poll(
            poll.question,
            [InputPollOption(text=poll.options[0][:100]), InputPollOption(text=poll.options[1][:100])],
            is_anonymous=True,
            reply_markup=build_keyboard()
        )
    except Exception as e:
        await message.reply(str(e))
