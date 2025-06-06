from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import CHANNEL_CHATID

router = Router()


@router.callback_query(F.data == 'delete')
async def delete_post(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.answer('Удалено')


@router.callback_query(F.data == 'send')
async def send_post(callback: CallbackQuery) -> None:
    await callback.message.copy_to(CHANNEL_CHATID)
    await callback.message.delete()
    await callback.answer('Отправлено')
