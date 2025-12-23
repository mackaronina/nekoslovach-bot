from aiogram.types import Update
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from app.config import SETTINGS
from app.dependencies import CurrentBot, CurrentDispatcher

router = APIRouter()


@router.post(f'/{SETTINGS.BOT_TOKEN.get_secret_value()}', include_in_schema=False)
async def webhook(request: Request, bot: CurrentBot, dispatcher: CurrentDispatcher) -> None:
    update = Update.model_validate(await request.json(), context={'bot': bot})
    await dispatcher.feed_update(bot, update)


@router.get('/')
async def read_root() -> HTMLResponse:
    return HTMLResponse(content='Main page')
