from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def keyboard_post_to_channel() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='✅', callback_data='send'),
        InlineKeyboardButton(text='❌', callback_data='cancel')
    )
    return builder.as_markup()


def keyboard_admin_confirmation(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='✅', callback_data=AdminConfirmCallbackFactory(action='accept', user_id=user_id)),
    builder.button(text='❌', callback_data=AdminConfirmCallbackFactory(action='decline', user_id=user_id)),
    builder.button(text='🔐 Забанить', callback_data=AdminConfirmCallbackFactory(action='ban', user_id=user_id))
    builder.adjust(2)
    return builder.as_markup()


class AdminConfirmCallbackFactory(CallbackData, prefix='admin'):
    action: str
    user_id: int
