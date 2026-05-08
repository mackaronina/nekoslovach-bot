from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.config import SETTINGS
from app.utils.dao import UserDAO

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message) -> None:
    await message.reply('Скинь мне в личку фото или текст и я сделаю из них новость для канала')


@router.message(Command('unban'), F.chat.id == SETTINGS.ADMIN_CHAT_ID)
async def cmd_unban(message: Message, command: CommandObject, bot: Bot) -> None:
    if command.args is None:
        await message.answer('Формат команды: /unban [user_id]')
        return
    try:
        user_id = int(command.args)
    except ValueError:
        await message.answer('Неправильный user_id')
        return
    await UserDAO.unban(user_id)
    await message.answer('Пользователь успешно разбанен')
    await bot.send_message(user_id, 'Вас разбанили')
