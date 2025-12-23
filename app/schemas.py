from typing import TypedDict

from aiogram.types import InputPollOption
from openai import BaseModel


class NewModel(BaseModel):
    title: str
    text: str


class PollModel(BaseModel):
    question: str
    options: list[str]


class PollDict(TypedDict):
    question: str
    options: list[InputPollOption]
    is_anonymous: bool
