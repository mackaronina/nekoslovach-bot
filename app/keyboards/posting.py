from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import SETTINGS


def get_posting_keyboard() -> InlineKeyboardMarkup:
    if SETTINGS.POSTING_CONFIRMATION:
        return keyboard_post_to_channel_with_confirmation()
    else:
        return keyboard_post_to_channel()


def keyboard_post_to_channel() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='✅', callback_data='send'),
        InlineKeyboardButton(text='❌', callback_data='cancel')
    )
    return builder.as_markup()


def keyboard_post_to_channel_with_confirmation() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='✅', callback_data='send_confirm'),
        InlineKeyboardButton(text='❌', callback_data='cancel')
    )
    return builder.as_markup()
