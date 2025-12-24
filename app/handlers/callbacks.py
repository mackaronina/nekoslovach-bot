from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.config import SETTINGS
from app.keyboards.posting import keyboard_post_to_channel
from app.utils.log import log_send_post, log_cancel_post

router = Router()


@router.callback_query(F.data == 'cancel')
async def cancel_post(callback: CallbackQuery) -> None:
    log_cancel_post(callback)
    await callback.answer('Отменено')
    await callback.message.delete()


@router.callback_query(F.data == 'send')
async def send_post(callback: CallbackQuery) -> None:
    log_send_post(callback)
    await callback.message.copy_to(SETTINGS.CHANNEL_CHAT_ID)
    await callback.answer('Отправлено')
    await callback.message.delete()


@router.callback_query(F.data == 'send_confirm')
async def send_to_confirm(callback: CallbackQuery) -> None:
    log_send_post(callback, True)
    await callback.message.copy_to(SETTINGS.ADMIN_CHAT_ID, reply_markup=keyboard_post_to_channel())
    await callback.answer('Отправлено на рассмотрение', show_alert=True)
    await callback.message.delete()
