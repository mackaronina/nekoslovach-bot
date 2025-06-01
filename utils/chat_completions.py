from typing import List

from openai import BaseModel, AsyncOpenAI

from config import LORE, MODEL_NAME, TEMPERATURE


class NewModel(BaseModel):
    title: str
    text: str


class PollModel(BaseModel):
    question: str
    options: List[str]


async def create_chat_completion_img(ai_client: AsyncOpenAI, prompt: str, img_url: str) -> str:
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


async def create_chat_completion_text(ai_client: AsyncOpenAI, prompt: str) -> str:
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
