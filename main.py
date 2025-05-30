import asyncio
import json
import logging
import random
import time
import traceback
from datetime import datetime
from typing import List, Tuple

import uvicorn
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.types import Message, ErrorEvent, BufferedInputFile, InputPollOption, Update, InlineKeyboardButton, \
    CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from openai import AsyncOpenAI, BaseModel

from config import *

ai_client = AsyncOpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_KEY)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))
dp = Dispatcher()

app = FastAPI()


class NewModel(BaseModel):
    title: str
    text: str


class PollModel(BaseModel):
    question: str
    options: List[str]


@dp.message(Command("start"))
async def msg_start(message: Message) -> None:
    await message.reply("Скинь мне фото или текст и я сделаю из них новость. Славься Некославия!")


@dp.error()
async def error_handler(event: ErrorEvent) -> None:
    await bot.send_document(
        REPORT_CHATID,
        BufferedInputFile(traceback.format_exc().encode('utf8'), filename="error.txt"),
        caption=str(event.exception)
    )


@dp.message(F.photo, F.caption, F.chat.type == "private")
@dp.message(F.photo, F.chat.type == "private")
@dp.message(F.text, F.chat.type == "private")
async def msg_private(message: Message) -> None:
    try:
        await create_new_and_poll(message)
    except Exception as e:
        await message.reply(str(e))


@dp.callback_query(F.data == "delete")
async def delete_post(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.answer("Удалено")


@dp.callback_query(F.data == "send")
async def send_post(callback: CallbackQuery) -> None:
    await callback.message.copy_to(CHANNEL_CHATID)
    await callback.message.delete()
    await callback.answer("Отправлено")


def cur_date() -> str:
    return datetime.fromtimestamp(time.time() + TIMESTAMP).strftime("%d.%m.%Y")


def news_text(new: NewModel, new_tag: str) -> str:
    return f"⚡️<b>{new.title}</b>\n\n{new.text}\n\n#{new_tag.replace(' ', '_').replace('-', '_')}"


def build_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅", callback_data="send"),
        InlineKeyboardButton(text="❌", callback_data="delete")
    )
    return builder.as_markup()


async def create_new_and_poll(message: Message) -> None:
    if message.caption and message.photo:
        new = await generate_new_from_img_and_caption(message.photo[-1].file_id, message.caption)
        await message.answer_photo(message.photo[-1].file_id, caption=news_text(new, 'предложка'),
                                   reply_markup=build_keyboard())
    elif message.photo:
        new = await generate_new_from_img(message.photo[-1].file_id)
        await message.answer_photo(message.photo[-1].file_id, caption=news_text(new, 'предложка'),
                                   reply_markup=build_keyboard())
    else:
        new = await generate_new_from_text(message.text)
        await message.answer(news_text(new, 'предложка'), reply_markup=build_keyboard())
    poll = await generate_poll(new)
    await message.answer_poll(
        poll.question,
        [InputPollOption(text=poll.options[0][:100]), InputPollOption(text=poll.options[1][:100])],
        is_anonymous=True,
        reply_markup=build_keyboard()
    )


async def get_photo_url(file_id: str) -> str:
    file_info = await bot.get_file(file_id)
    return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"


async def create_chat_completion_img(prompt: str, img_url: str) -> str:
    chat_completion = await ai_client.chat.completions.create(
        messages=[
            {"role": "system",
             "content": LORE},
            {"role": "user",
             "content": [
                 {
                     "type": "text",
                     "text": prompt
                 },
                 {
                     "type": "image_url",
                     "image_url": {
                         "url": img_url
                     }
                 }
             ]}
        ],
        response_format={"type": "json_object"},
        model=MODEL_NAME,
        temperature=TEMPERATURE
    )
    return chat_completion.choices[0].message.content


async def generate_new_from_img_and_caption(file_id: str, caption: str) -> NewModel:
    url = await get_photo_url(file_id)
    content = await create_chat_completion_img(
        PHOTO_AND_CAPTION_PROMPT.format(
            title=caption,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        ),
        url
    )
    return NewModel.model_validate_json(content)


async def generate_new_from_img(file_id: str) -> NewModel:
    url = await get_photo_url(file_id)
    content = await create_chat_completion_img(
        PHOTO_PROMPT.format(
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        ),
        url
    )
    return NewModel.model_validate_json(content)


async def create_chat_completion_text(prompt: str) -> str:
    chat_completion = await ai_client.chat.completions.create(
        messages=[
            {"role": "system",
             "content": LORE},
            {"role": "user",
             "content": prompt}
        ],
        response_format={"type": "json_object"},
        model=MODEL_NAME,
        temperature=TEMPERATURE
    )
    return chat_completion.choices[0].message.content


async def generate_new_from_text(text: str) -> NewModel:
    content = await create_chat_completion_text(
        TEXT_PROMPT.format(
            title=text,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        )
    )
    return NewModel.model_validate_json(content)


async def generate_new_from_tag() -> Tuple[NewModel, str]:
    new_tag = random.choice(NEW_TAGS)
    content = await create_chat_completion_text(
        TAG_PROMPT.format(
            tag=new_tag,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        )
    )
    return NewModel.model_validate_json(content), new_tag


async def generate_poll(new: NewModel) -> PollModel:
    content = await create_chat_completion_text(
        POLL_PROMPT.format(
            title=new.title,
            text=new.text,
            schema=json.dumps(PollModel.model_json_schema(), indent=2)
        )
    )
    return PollModel.model_validate_json(content)


async def job_post_news() -> None:
    new, new_tag = await generate_new_from_tag()
    await bot.send_message(CHANNEL_CHATID, news_text(new, new_tag))
    poll = await generate_poll(new)
    await bot.send_poll(
        CHANNEL_CHATID,
        poll.question,
        [InputPollOption(text=poll.options[0][:100]), InputPollOption(text=poll.options[1][:100])],
        is_anonymous=True
    )


@app.post(f"/{BOT_TOKEN}")
async def webhook(request: Request) -> None:
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)


@app.get("/")
async def read_root() -> HTMLResponse:
    return HTMLResponse(content="ok")


async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job_post_news, 'interval', hours=12)
    scheduler.start()
    await bot.send_message(REPORT_CHATID, 'Запущено')
    await bot.delete_webhook()
    # await dp.start_polling(bot)
    await bot.set_webhook(url=f"{APP_URL}/{BOT_TOKEN}", drop_pending_updates=True)
    await uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=80)).serve()


if __name__ == '__main__':
    asyncio.run(main())
