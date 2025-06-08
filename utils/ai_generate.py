import html
import json
import random
import time
from datetime import datetime
from typing import TypedDict, List

from aiogram.types import Message, InputPollOption
from openai import AsyncOpenAI, BaseModel

from config import TIMESTAMP, BOT_TOKEN, NEW_TAGS, NEW_DEFAULT_TAG
from prompts import NEW_PHOTO_AND_CAPTION_PROMPT, NEW_PHOTO_PROMPT, NEW_TEXT_PROMPT, NEW_TAG_PROMPT, POLL_PROMPT, \
    COMMENT_TEXT_PROMPT, COMMENT_PHOTO_PROMPT, COMMENT_PHOTO_AND_CAPTION_PROMPT
from utils.api_calls import chat_completion_img, chat_completion_text


class NewModel(BaseModel):
    title: str
    text: str


class PollModel(BaseModel):
    question: str
    options: List[str]


class PollDict(TypedDict):
    question: str
    options: List[InputPollOption]
    is_anonymous: bool


def cur_date() -> str:
    return datetime.fromtimestamp(time.time() + TIMESTAMP).strftime('%d.%m.%Y')


def new_to_text(new: NewModel, new_tag: str) -> str:
    new_tag = new_tag.replace(' ', '_').replace('-', '_')
    return f'⚡️<b>{html.escape(new.title)}</b>\n\n{html.escape(new.text)}\n\n#{html.escape(new_tag)}'


async def get_img_url(message: Message) -> str:
    if message.photo is not None:
        file_id = message.photo[-1].file_id
    else:
        file_id = message.sticker.file_id
    file_info = await message.bot.get_file(file_id)
    return f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}'


def postprocess_comment(text: str) -> str:
    text = text.replace("'", '').replace('"', '').strip('. ')
    return html.escape(text[:1].upper() + text[1:])


def poll_to_dict(poll: PollModel) -> PollDict:
    return {
        'question': html.escape(poll.question),
        'options': [InputPollOption(text=html.escape(poll.options[0][:100])),
                    InputPollOption(text=html.escape(poll.options[1][:100]))],
        'is_anonymous': True,
    }


async def generate_new_from_img_and_caption(ai_client: AsyncOpenAI, message: Message) -> str:
    url = await get_img_url(message)
    content = await chat_completion_img(
        ai_client,
        NEW_PHOTO_AND_CAPTION_PROMPT.format(
            title=message.text or message.caption,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema())
        ),
        url
    )
    new = NewModel.model_validate_json(content)
    return new_to_text(new, NEW_DEFAULT_TAG)


async def generate_new_from_img(ai_client: AsyncOpenAI, message: Message) -> str:
    url = await get_img_url(message)
    content = await chat_completion_img(
        ai_client,
        NEW_PHOTO_PROMPT.format(
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema())
        ),
        url
    )
    new = NewModel.model_validate_json(content)
    return new_to_text(new, NEW_DEFAULT_TAG)


async def generate_new_from_text(ai_client: AsyncOpenAI, message: Message) -> str:
    content = await chat_completion_text(
        ai_client,
        NEW_TEXT_PROMPT.format(
            title=message.text or message.caption,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema())
        )
    )
    new = NewModel.model_validate_json(content)
    return new_to_text(new, NEW_DEFAULT_TAG)


async def generate_new_from_tag(ai_client: AsyncOpenAI) -> str:
    new_tag = random.choice(NEW_TAGS)
    content = await chat_completion_text(
        ai_client,
        NEW_TAG_PROMPT.format(
            tag=new_tag,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema())
        )
    )
    new = NewModel.model_validate_json(content)
    return new_to_text(new, new_tag)


async def generate_poll(ai_client: AsyncOpenAI, new_text: str) -> PollDict:
    content = await chat_completion_text(
        ai_client,
        POLL_PROMPT.format(
            new_text=new_text.replace('\n', ' '),
            schema=json.dumps(PollModel.model_json_schema())
        )
    )
    poll = PollModel.model_validate_json(content)
    return poll_to_dict(poll)


async def generate_reply_comment_text(ai_client: AsyncOpenAI, message: Message, post_text: str) -> str:
    text = await chat_completion_text(
        ai_client,
        COMMENT_TEXT_PROMPT.format(
            post_text=post_text.replace('\n', ' '),
            user_name=message.from_user.full_name,
            comment_text=message.text or message.caption
        ),
        response_format='text'
    )
    return postprocess_comment(text)


async def generate_reply_comment_img(ai_client: AsyncOpenAI, message: Message, post_text: str) -> str:
    url = await get_img_url(message)
    text = await chat_completion_img(
        ai_client,
        COMMENT_PHOTO_PROMPT.format(
            post_text=post_text.replace('\n', ' '),
            user_name=message.from_user.full_name
        ),
        url,
        response_format='text'
    )
    return postprocess_comment(text)


async def generate_reply_comment_img_and_caption(ai_client: AsyncOpenAI, message: Message, post_text: str) -> str:
    url = await get_img_url(message)
    text = await chat_completion_img(
        ai_client,
        COMMENT_PHOTO_AND_CAPTION_PROMPT.format(
            post_text=post_text.replace('\n', ' '),
            user_name=message.from_user.full_name,
            comment_text=message.text or message.caption
        ),
        url,
        response_format='text'
    )
    return postprocess_comment(text)
