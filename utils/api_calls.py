import logging

from openai import AsyncOpenAI

from config import MODEL_NAME, TEMPERATURE
from prompts import SYSTEM_PROMPT


async def chat_completion_img(ai_client: AsyncOpenAI, prompt: str, img_url: str,
                              response_format: str = 'json_object') -> str:
    logging.info(f'Sending prompt: {prompt}')
    chat_completion = await ai_client.chat.completions.create(
        messages=[
            {'role': 'system',
             'content': SYSTEM_PROMPT},
            {'role': 'user',
             'content': [
                 {
                     'type': 'text',
                     'text': prompt
                 },
                 {
                     'type': 'image_url',
                     'image_url': {
                         'url': img_url
                     }
                 }
             ]}
        ],
        response_format={'type': response_format},
        model=MODEL_NAME,
        temperature=TEMPERATURE
    )
    return chat_completion.choices[0].message.content


async def chat_completion_text(ai_client: AsyncOpenAI, prompt: str, response_format: str = 'json_object') -> str:
    logging.info(f'Sending prompt: {prompt}')
    chat_completion = await ai_client.chat.completions.create(
        messages=[
            {'role': 'system',
             'content': SYSTEM_PROMPT},
            {'role': 'user',
             'content': prompt}
        ],
        response_format={'type': response_format},
        model=MODEL_NAME,
        temperature=TEMPERATURE
    )
    return chat_completion.choices[0].message.content
