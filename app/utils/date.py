import time
from datetime import datetime

from app.config import SETTINGS


def cur_date() -> str:
    return datetime.fromtimestamp(time.time() + SETTINGS.TIMESTAMP).strftime('%d.%m.%Y')
