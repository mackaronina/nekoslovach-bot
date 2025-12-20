import asyncio
import logging

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from openai import AsyncOpenAI

from config import SETTINGS
from handlers import private_messages, callbacks, commands, errors, comments_messages
from utils.jobs import job_post_news


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

    async def webhook(request: Request) -> None:
        update = Update.model_validate(await request.json(), context={'bot': bot})
        await dp.feed_update(bot, update)

    async def read_root() -> HTMLResponse:
        return HTMLResponse(content='ok')

    app.add_api_route('/', endpoint=read_root, methods=['GET'])
    app.add_api_route(f'/{SETTINGS.BOT_TOKEN.get_secret_value()}', endpoint=webhook, methods=['POST'],
                      include_in_schema=False)

    scheduler = AsyncIOScheduler()
    if SETTINGS.AUTO_POSTING:
        scheduler.add_job(job_post_news, 'interval', (bot, ai_client), hours=SETTINGS.POST_INTERVAL)
    scheduler.start()

    await bot.delete_webhook()
    # Uncomment for polling
    # await dp.start_polling(bot)
    await bot.set_webhook(url=f'{SETTINGS.WEBHOOK_DOMAIN}/{SETTINGS.BOT_TOKEN.get_secret_value()}',
                          drop_pending_updates=True)
    logging.info('Bot started')
    await uvicorn.Server(uvicorn.Config(app, host=SETTINGS.HOST, port=SETTINGS.PORT)).serve()


if __name__ == '__main__':
    asyncio.run(main())
