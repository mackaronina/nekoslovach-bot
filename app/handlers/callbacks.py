from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from app.config import SETTINGS
from app.keyboards.posting import keyboard_admin_confirmation, AdminConfirmCallbackFactory
from app.middlewares.check_ban import CheckBanMiddleware
from app.utils.dao import UserDAO
from app.utils.log import log_send_post, log_cancel_post

router = Router()
router.callback_query.middleware(CheckBanMiddleware())


@router.callback_query(F.data == 'cancel')
async def cancel_post(callback: CallbackQuery) -> None:
    log_cancel_post(callback)
    await callback.answer('Отменено')
    await callback.message.delete()


@router.callback_query(F.data == 'send')
async def send_post(callback: CallbackQuery) -> None:
    log_send_post(callback)
    if SETTINGS.POSTING_CONFIRMATION:
        await callback.message.copy_to(SETTINGS.ADMIN_CHAT_ID,
                                       reply_markup=keyboard_admin_confirmation(callback.from_user.id))
        await callback.answer('Отправлено на рассмотрение', show_alert=True)
    else:
        await callback.message.copy_to(SETTINGS.CHANNEL_CHAT_ID)
        await callback.answer('Отправлено')
    await callback.message.delete()


@router.callback_query(AdminConfirmCallbackFactory.filter())
async def admin_confirmation(callback: CallbackQuery, callback_data: AdminConfirmCallbackFactory, bot: Bot):
    user_id = callback_data.user_id
    if callback_data.action == 'accept':
        await callback.message.copy_to(SETTINGS.CHANNEL_CHAT_ID)
        await bot.send_message(user_id, 'Ваша новость принята')
        await callback.answer('Отправлено')
    elif callback_data.action == 'decline':
        await callback.answer('Отклонено')
        await bot.send_message(user_id, 'Ваша новость отклонена')
    elif callback_data.action == 'ban':
        await UserDAO.ban(user_id)
        await callback.answer('Забанен')
        await bot.send_message(
            callback.message.chat.id,
            f'Пользователь забанен. Чтобы разбанить его используйте команду <code>/unban {user_id}</code>'
        )
        await bot.send_message(user_id, 'Вы были забанены и больше не можете пользоваться ботом')
    await callback.message.delete()
