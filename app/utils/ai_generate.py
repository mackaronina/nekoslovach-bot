import random

from aiogram.types import Message
from openai import AsyncOpenAI

from app.config import SETTINGS
from app.prompts import NEW_PHOTO_PROMPT, POLL_PROMPT, COMMENT_TEXT_PROMPT, COMMENT_PHOTO_PROMPT, \
    COMMENT_PHOTO_AND_CAPTION_PROMPT, NEW_SCHEMA_DESCRIPTION, POLL_SCHEMA_DESCRIPTION, COMMENT_SCHEMA_DESCRIPTION, \
    NEW_PHOTO_AND_TITLE_PROMPT, NEW_TITLE_PROMPT, NEW_TOPIC_PROMPT
from app.schemas import NewModel, PollModel, PollDict, CommentModel
from app.utils.api_calls import chat_completion_img, chat_completion_text
from app.utils.date import cur_date
from app.utils.images import get_img_as_base64


async def generate_new_from_img_and_title(ai_client: AsyncOpenAI, message: Message) -> str:
    base64_image = await get_img_as_base64(message)
    content = await chat_completion_img(
        ai_client,
        NEW_PHOTO_AND_TITLE_PROMPT.format(
            title=message.text or message.caption,
            date=cur_date(),
            schema_description=NEW_SCHEMA_DESCRIPTION
        ),
        base64_image
    )
    new = NewModel.model_validate_json(content)
    new.tags.append(SETTINGS.TAGS.BY_USER)
    return str(new)


async def generate_new_from_img(ai_client: AsyncOpenAI, message: Message) -> str:
    base64_image = await get_img_as_base64(message)
    content = await chat_completion_img(
        ai_client,
        NEW_PHOTO_PROMPT.format(
            date=cur_date(),
            schema_description=NEW_SCHEMA_DESCRIPTION
        ),
        base64_image
    )
    new = NewModel.model_validate_json(content)
    new.tags.append(SETTINGS.TAGS.BY_USER)
    return str(new)


async def generate_new_from_title(ai_client: AsyncOpenAI, message: Message) -> str:
    content = await chat_completion_text(
        ai_client,
        NEW_TITLE_PROMPT.format(
            title=message.text or message.caption,
            date=cur_date(),
            schema_description=NEW_SCHEMA_DESCRIPTION
        )
    )
    new = NewModel.model_validate_json(content)
    new.tags.append(SETTINGS.TAGS.BY_USER)
    return str(new)


async def generate_new_from_topic(ai_client: AsyncOpenAI) -> str:
    topic = random.choice(SETTINGS.TAGS.ALL)
    content = await chat_completion_text(
        ai_client,
        NEW_TOPIC_PROMPT.format(
            topic=topic,
            date=cur_date(),
            schema_description=NEW_SCHEMA_DESCRIPTION
        )
    )
    new = NewModel.model_validate_json(content)
    return str(new)


async def generate_poll(ai_client: AsyncOpenAI, new_text: str) -> PollDict:
    content = await chat_completion_text(
        ai_client,
        POLL_PROMPT.format(
            new_text=new_text.replace('\n', ' '),
            schema_description=POLL_SCHEMA_DESCRIPTION
        )
    )
    poll = PollModel.model_validate_json(content)
    return poll.as_dict()


async def generate_reply_comment_text(ai_client: AsyncOpenAI, message: Message, post_text: str) -> str:
    content = await chat_completion_text(
        ai_client,
        COMMENT_TEXT_PROMPT.format(
            post_text=post_text.replace('\n', ' '),
            user_name=message.from_user.full_name,
            comment_text=message.text or message.caption,
            schema_description=COMMENT_SCHEMA_DESCRIPTION
        )
    )
    comment = CommentModel.model_validate_json(content)
    return str(comment)


async def generate_reply_comment_img(ai_client: AsyncOpenAI, message: Message, post_text: str) -> str:
    base64_image = await get_img_as_base64(message)
    content = await chat_completion_img(
        ai_client,
        COMMENT_PHOTO_PROMPT.format(
            post_text=post_text.replace('\n', ' '),
            user_name=message.from_user.full_name,
            schema_description=COMMENT_SCHEMA_DESCRIPTION
        ),
        base64_image,
    )
    comment = CommentModel.model_validate_json(content)
    return str(comment)


async def generate_reply_comment_img_and_caption(ai_client: AsyncOpenAI, message: Message, post_text: str) -> str:
    base64_image = await get_img_as_base64(message)
    content = await chat_completion_img(
        ai_client,
        COMMENT_PHOTO_AND_CAPTION_PROMPT.format(
            post_text=post_text.replace('\n', ' '),
            user_name=message.from_user.full_name,
            comment_text=message.text or message.caption,
            schema_description=COMMENT_SCHEMA_DESCRIPTION
        ),
        base64_image,
    )
    comment = CommentModel.model_validate_json(content)
    return str(comment)
