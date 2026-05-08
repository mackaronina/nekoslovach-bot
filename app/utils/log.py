import logging

from aiogram.types import CallbackQuery

from app.config import SETTINGS


def log_send_post(callback: CallbackQuery) -> None:
    if callback.message.text is not None or callback.message.caption is not None:
        logging.info(
            f'User {callback.from_user.id} {"sending for confirmation" if SETTINGS.POSTING_CONFIRMATION else "posting"} new with text: {callback.message.text or callback.message.caption}'
        )
    elif callback.message.poll is not None:
        logging.info(
            f'User {callback.from_user.id} {"sending for confirmation" if SETTINGS.POSTING_CONFIRMATION else "posting"} poll with question: {callback.message.poll.question}'
        )


def log_cancel_post(callback: CallbackQuery) -> None:
    if callback.message.text is not None or callback.message.caption is not None:
        logging.info(
            f'User {callback.from_user.id} canceling new with text: {callback.message.text or callback.message.caption}'
        )
    elif callback.message.poll is not None:
        logging.info(
            f'User {callback.from_user.id} canceling poll with question: {callback.message.poll.question}'
        )
