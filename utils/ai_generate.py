import json
import random
import time
from datetime import datetime
from typing import Tuple

from aiogram import Bot
from aiogram.types import Message
from openai import AsyncOpenAI

from config import TIMESTAMP, BOT_TOKEN, NEW_PHOTO_AND_CAPTION_PROMPT, NEW_PHOTO_PROMPT, NEW_TEXT_PROMPT, NEW_TAGS, \
    NEW_TAG_PROMPT, POLL_PROMPT, REPLY_COMMENT_POLL_PROMPT, REPLY_COMMENT_NEW_PROMPT, REPLY_COMMENT_DIALOG_PROMPT
from utils.api_calls import chat_completion_img, chat_completion_text
from utils.models import NewModel, PollModel


def cur_date() -> str:
    return datetime.fromtimestamp(time.time() + TIMESTAMP).strftime("%d.%m.%Y")


def news_text(new: NewModel, new_tag: str) -> str:
    return f"⚡️<b>{new.title}</b>\n\n{new.text}\n\n#{new_tag.replace(' ', '_').replace('-', '_')}"


async def get_photo_url(bot: Bot, file_id: str) -> str:
    file_info = await bot.get_file(file_id)
    return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"


async def generate_new_from_img_and_caption(bot: Bot, ai_client: AsyncOpenAI, file_id: str, caption: str) -> NewModel:
    url = await get_photo_url(bot, file_id)
    content = await chat_completion_img(
        ai_client,
        NEW_PHOTO_AND_CAPTION_PROMPT.format(
            title=caption,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        ),
        url
    )
    return NewModel.model_validate_json(content)


async def generate_new_from_img(bot: Bot, ai_client: AsyncOpenAI, file_id: str) -> NewModel:
    url = await get_photo_url(bot, file_id)
    content = await chat_completion_img(
        ai_client,
        NEW_PHOTO_PROMPT.format(
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        ),
        url
    )
    return NewModel.model_validate_json(content)


async def generate_new_from_text(ai_client: AsyncOpenAI, text: str) -> NewModel:
    content = await chat_completion_text(
        ai_client,
        NEW_TEXT_PROMPT.format(
            title=text,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        )
    )
    return NewModel.model_validate_json(content)


async def generate_new_from_tag(ai_client: AsyncOpenAI) -> Tuple[NewModel, str]:
    new_tag = random.choice(NEW_TAGS)
    content = await chat_completion_text(
        ai_client,
        NEW_TAG_PROMPT.format(
            tag=new_tag,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema(), indent=2)
        )
    )
    return NewModel.model_validate_json(content), new_tag


async def generate_poll(ai_client: AsyncOpenAI, new: NewModel) -> PollModel:
    content = await chat_completion_text(
        ai_client,
        POLL_PROMPT.format(
            title=new.title,
            text=new.text,
            schema=json.dumps(PollModel.model_json_schema(), indent=2)
        )
    )
    return PollModel.model_validate_json(content)


async def generate_reply_to_comment_new(ai_client: AsyncOpenAI, message: Message) -> str:
    return await chat_completion_text(
        ai_client,
        REPLY_COMMENT_NEW_PROMPT.format(
            new_text=message.reply_to_message.text or message.reply_to_message.caption,
            user_name=message.from_user.full_name,
            comment_text=message.text or message.caption
        ),
        response_format="text"
    )


async def generate_reply_to_comment_poll(ai_client: AsyncOpenAI, message: Message) -> str:
    return await chat_completion_text(
        ai_client,
        REPLY_COMMENT_POLL_PROMPT.format(
            poll_question=message.reply_to_message.poll.question,
            user_name=message.from_user.full_name,
            comment_text=message.text or message.caption,
        ),
        response_format="text"
    )


async def generate_reply_to_comment_dialog(ai_client: AsyncOpenAI, message: Message) -> str:
    return await chat_completion_text(
        ai_client,
        REPLY_COMMENT_DIALOG_PROMPT.format(
            reply_to_text=message.reply_to_message.text or message.reply_to_message.caption,
            user_name=message.from_user.full_name,
            comment_text=message.text or message.caption,
        ),
        response_format="text"
    )
