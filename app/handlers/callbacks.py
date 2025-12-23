import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.config import SETTINGS

router = Router()


@router.callback_query(F.data == 'delete')
async def delete_post(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.answer('Удалено')


@router.callback_query(F.data == 'send')
async def send_post(callback: CallbackQuery) -> None:
    if callback.message.text is not None or callback.message.caption is not None:
        logging.info(
            f'User {callback.from_user.id} posting new with text: {callback.message.text or callback.message.caption}')
    elif callback.message.poll is not None:
        logging.info(f'User {callback.from_user.id} posting poll with question: {callback.message.poll.question}')
    await callback.message.copy_to(SETTINGS.CHANNEL_CHAT_ID)
    await callback.message.delete()
    await callback.answer('Отправлено')
