import logging
import traceback

from aiogram import Router, Bot
from aiogram.types import ErrorEvent, BufferedInputFile

from config import REPORT_CHATID

router = Router()


@router.error()
async def error_handler(event: ErrorEvent, bot: Bot) -> None:
    await bot.send_document(
        REPORT_CHATID,
        BufferedInputFile(traceback.format_exc().encode('utf8'), filename='error.txt'),
        caption=str(event.exception)
    )
    logging.exception(str(event.exception))
