import base64
from io import BytesIO

from aiogram.types import Message


async def get_img_as_base64(message: Message) -> str:
    bot = message.bot
    if message.photo is not None:
        file_id = message.photo[-1].file_id
    else:
        file_id = message.sticker.file_id
    buffer = BytesIO()
    await bot.download(file_id, buffer)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')
