import asyncio
import logging

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from openai import AsyncOpenAI

from app.api import webhook
from app.config import SETTINGS
from app.handlers import private_messages, commands, errors, callbacks, comments_messages
from app.utils.jobs import job_post_news


async def main() -> None:
    ai_client = AsyncOpenAI(base_url=SETTINGS.OPENAI.URL, api_key=SETTINGS.OPENAI.TOKEN.get_secret_value())

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    bot = Bot(token=SETTINGS.BOT_TOKEN.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))
    dp = Dispatcher()
    dp['comment_ids'] = {}
    dp['post_texts'] = {}
    dp['ai_client'] = ai_client
    dp.include_routers(callbacks.router, commands.router, errors.router, private_messages.router,
                       comments_messages.router)

    app = FastAPI()

    app.include_router(webhook.router)
    app.state.bot = bot
    app.state.dp = dp

    scheduler = AsyncIOScheduler(timezone=SETTINGS.TIME_ZONE)
    if SETTINGS.AUTO_POSTING:
        scheduler.add_job(job_post_news, 'interval', (bot, ai_client), hours=SETTINGS.POST_INTERVAL_HOURS)
    scheduler.start()

    await bot.delete_webhook()
    logging.info('Bot started')
    if SETTINGS.USE_POLLING:
        await dp.start_polling(bot)
    else:
        await bot.set_webhook(url=f'{SETTINGS.WEBHOOK_DOMAIN}/{SETTINGS.BOT_TOKEN.get_secret_value()}',
                              drop_pending_updates=True)
        await uvicorn.Server(uvicorn.Config(app, host=SETTINGS.HOST, port=SETTINGS.PORT)).serve()


if __name__ == '__main__':
    asyncio.run(main())
