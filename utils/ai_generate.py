import json
import random

from aiogram.types import Message
from openai import AsyncOpenAI

from config import SETTINGS
from prompts import NEW_PHOTO_AND_CAPTION_PROMPT, NEW_PHOTO_PROMPT, NEW_TEXT_PROMPT, NEW_TAG_PROMPT, POLL_PROMPT, \
    COMMENT_TEXT_PROMPT, COMMENT_PHOTO_PROMPT, COMMENT_PHOTO_AND_CAPTION_PROMPT
from schemas import NewModel, PollModel, PollDict
from utils.api_calls import chat_completion_img, chat_completion_text
from utils.date import cur_date
from utils.images import get_img_as_base64
from utils.text import new_to_text, postprocess_comment, poll_model_to_dict


async def generate_new_from_img_and_caption(ai_client: AsyncOpenAI, message: Message) -> str:
    base64_image = await get_img_as_base64(message)
    content = await chat_completion_img(
        ai_client,
        NEW_PHOTO_AND_CAPTION_PROMPT.format(
            title=message.text or message.caption,
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema())
        ),
        base64_image
    )
    new = NewModel.model_validate_json(content)
    return new_to_text(new, SETTINGS.TAGS.DEFAULT)


async def generate_new_from_img(ai_client: AsyncOpenAI, message: Message) -> str:
    base64_image = await get_img_as_base64(message)
    content = await chat_completion_img(
        ai_client,
        NEW_PHOTO_PROMPT.format(
            date=cur_date(),
            schema=json.dumps(NewModel.model_json_schema())
        ),
        base64_image
    )
    new = NewModel.model_validate_json(content)
    return new_to_text(new, SETTINGS.TAGS.DEFAULT)


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
    return new_to_text(new, SETTINGS.TAGS.DEFAULT)


async def generate_new_from_tag(ai_client: AsyncOpenAI) -> str:
    new_tag = random.choice(SETTINGS.TAGS.ALL)
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
    return poll_model_to_dict(poll)


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
    base64_image = await get_img_as_base64(message)
    text = await chat_completion_img(
        ai_client,
        COMMENT_PHOTO_PROMPT.format(
            post_text=post_text.replace('\n', ' '),
            user_name=message.from_user.full_name
        ),
        base64_image,
        response_format='text'
    )
    return postprocess_comment(text)


async def generate_reply_comment_img_and_caption(ai_client: AsyncOpenAI, message: Message, post_text: str) -> str:
    base64_image = await get_img_as_base64(message)
    text = await chat_completion_img(
        ai_client,
        COMMENT_PHOTO_AND_CAPTION_PROMPT.format(
            post_text=post_text.replace('\n', ' '),
            user_name=message.from_user.full_name,
            comment_text=message.text or message.caption
        ),
        base64_image,
        response_format='text'
    )
    return postprocess_comment(text)
