from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def msg_start(message: Message) -> None:
    await message.reply("Скинь мне в личку фото или текст и я сделаю из них новость для канала. Славься Некославия!")
