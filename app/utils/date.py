from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import SETTINGS


def cur_date() -> str:
    return datetime.now(ZoneInfo(SETTINGS.TIME_ZONE)).strftime('%d.%m.%Y')
