import html
from typing import TypedDict, Literal, Annotated

from aiogram.types import InputPollOption
from pydantic import Field, BaseModel

from app.config import SETTINGS


class NewModel(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    text: str = Field(min_length=1, max_length=800)
    tags: list[Literal[*SETTINGS.TAGS.ALL]] = Field(min_length=1, max_length=3)

    def __str__(self) -> str:
        tags = [f"#{html.escape(tag.replace(' ', '_').replace('-', '_'))}" for tag in self.tags]
        return f'⚡️<b>{html.escape(self.title)}</b>\n\n{html.escape(self.text)}\n\n{' '.join(tags)}'


class CommentModel(BaseModel):
    text: str = Field(min_length=1, max_length=1024)

    def __str__(self) -> str:
        text = self.text.replace("'", '').replace('"', '').strip('. ')
        return html.escape(text[:1].upper() + text[1:])


class PollDict(TypedDict):
    question: str
    options: list[InputPollOption]
    is_anonymous: bool


class PollModel(BaseModel):
    question: str = Field(min_length=1, max_length=255)
    options: list[Annotated[str, Field(min_length=1, max_length=100)]] = Field(min_length=2, max_length=2)

    def as_dict(self) -> PollDict:
        return {
            'question': html.escape(self.question),
            'options': [InputPollOption(text=html.escape(self.options[0])),
                        InputPollOption(text=html.escape(self.options[1]))],
            'is_anonymous': True,
        }
