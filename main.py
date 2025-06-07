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

from config import BOT_TOKEN, REPORT_CHATID, GROQ_KEY, APP_URL
from handlers import private_messages, callbacks, commands, errors, comments_messages
from utils.jobs import job_post_news


async def main() -> None:
    ai_client = AsyncOpenAI(base_url='https://api.groq.com/openai/v1', api_key=GROQ_KEY)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))
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
    app.add_api_route(f'/{BOT_TOKEN}', endpoint=webhook, methods=['POST'])

    scheduler = AsyncIOScheduler()
    scheduler.add_job(job_post_news, 'interval', (bot, ai_client), hours=12)
    scheduler.start()

    await bot.send_message(REPORT_CHATID, 'Запущено')
    await bot.delete_webhook()
    # Uncomment for polling
    # await dp.start_polling(bot)
    await bot.set_webhook(url=f'{APP_URL}/{BOT_TOKEN}', drop_pending_updates=True)
    await uvicorn.Server(uvicorn.Config(app, host='0.0.0.0', port=80)).serve()


if __name__ == '__main__':
    asyncio.run(main())
