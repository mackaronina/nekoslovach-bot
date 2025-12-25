import logging

from aiogram import Bot
from openai import AsyncOpenAI

from app.config import SETTINGS
from app.utils.ai_generate import generate_new_from_topic, generate_poll


async def job_post_news(bot: Bot, ai_client: AsyncOpenAI) -> None:
    new_text = await generate_new_from_topic(ai_client)
    logging.info(f'Automatic posting new with text: {new_text}')
    await bot.send_message(SETTINGS.CHANNEL_CHAT_ID, new_text)
    poll = await generate_poll(ai_client, new_text)
    logging.info(f'Automatic posting poll with question: {poll["question"]}')
    await bot.send_poll(SETTINGS.CHANNEL_CHAT_ID, **poll)
