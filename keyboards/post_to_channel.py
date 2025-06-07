from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def keyboard_post_to_channel() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='✅', callback_data='send'),
        InlineKeyboardButton(text='❌', callback_data='delete')
    )
    return builder.as_markup()
