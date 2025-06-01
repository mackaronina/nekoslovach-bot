import json
import random
import time
from datetime import datetime
from typing import Tuple

from aiogram import Bot
from openai import AsyncOpenAI

from config import TIMESTAMP, BOT_TOKEN, PHOTO_AND_CAPTION_PROMPT, PHOTO_PROMPT, TEXT_PROMPT, NEW_TAGS, TAG_PROMPT, \
    POLL_PROMPT
from utils.chat_completions import NewModel, create_chat_completion_img, create_chat_completion_text, PollModel


def cur_date() -> str:
    return datetime.fromtimestamp(time.time() + TIMESTAMP).strftime("%d.%m.%Y")


def news_text(new: NewModel, new_tag: str) -> str:
    return f"⚡️<b>{new.title}</b>\n\n{new.text}\n\n#{new_tag.replace(' ', '_').replace('-', '_')}"


async def get_photo_url(bot: Bot, file_id: str) -> str:
    file_info = await bot.get_file(file_id)
    return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"


async def generate_new_from_img_and_caption(bot: Bot, ai_client: AsyncOpenAI, file_id: str, caption: str) -> NewModel:
    url = await get_photo_url(bot, file_id)
    content = await create_chat_completion_img(
        ai_client,
        PHOTO_AND_CAPTION_PROMPT.format(
            title=caption,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        ),
        url
    )
    return NewModel.model_validate_json(content)


async def generate_new_from_img(bot: Bot, ai_client: AsyncOpenAI, file_id: str) -> NewModel:
    url = await get_photo_url(bot, file_id)
    content = await create_chat_completion_img(
        ai_client,
        PHOTO_PROMPT.format(
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        ),
        url
    )
    return NewModel.model_validate_json(content)


async def generate_new_from_text(ai_client: AsyncOpenAI, text: str) -> NewModel:
    content = await create_chat_completion_text(
        ai_client,
        TEXT_PROMPT.format(
            title=text,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        )
    )
    return NewModel.model_validate_json(content)


async def generate_new_from_tag(ai_client: AsyncOpenAI) -> Tuple[NewModel, str]:
    new_tag = random.choice(NEW_TAGS)
    content = await create_chat_completion_text(
        ai_client,
        TAG_PROMPT.format(
            tag=new_tag,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        )
    )
    return NewModel.model_validate_json(content), new_tag


async def generate_poll(ai_client: AsyncOpenAI, new: NewModel) -> PollModel:
    content = await create_chat_completion_text(
        ai_client,
        POLL_PROMPT.format(
            title=new.title,
            text=new.text,
            schema=json.dumps(PollModel.model_json_schema(), indent=2)
        )
    )
    return PollModel.model_validate_json(content)
