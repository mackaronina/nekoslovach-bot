from aiogram import Bot
from aiogram.types import InputPollOption
from openai import AsyncOpenAI

from config import CHANNEL_CHATID
from utils.generate_news import generate_new_from_tag, news_text, generate_poll


async def job_post_news(bot: Bot, ai_client: AsyncOpenAI) -> None:
    new, new_tag = await generate_new_from_tag(ai_client)
    await bot.send_message(CHANNEL_CHATID, news_text(new, new_tag))
    poll = await generate_poll(ai_client, new)
    await bot.send_poll(
        CHANNEL_CHATID,
        poll.question,
        [InputPollOption(text=poll.options[0][:100]), InputPollOption(text=poll.options[1][:100])],
        is_anonymous=True
    )
