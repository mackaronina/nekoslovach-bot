import logging

from aiogram import Bot
from openai import AsyncOpenAI

from config import settings
from utils.ai_generate import generate_new_from_tag, generate_poll


async def job_post_news(bot: Bot, ai_client: AsyncOpenAI) -> None:
    new_text = await generate_new_from_tag(ai_client)
    logging.info(f'Automatic posting new with text: {new_text}')
    await bot.send_message(settings.channel_chat_id, new_text)
    poll = await generate_poll(ai_client, new_text)
    logging.info(f'Automatic posting poll with question: {poll["question"]}')
    await bot.send_poll(settings.channel_chat_id, **poll)
