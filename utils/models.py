from typing import List

from openai import BaseModel


class NewModel(BaseModel):
    title: str
    text: str


class PollModel(BaseModel):
    question: str
    options: List[str]
