from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, func, JSON, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import SETTINGS

engine = create_async_engine(SETTINGS.POSTGRES.get_url() if not SETTINGS.USE_SQLITE else SETTINGS.SQLITE_URL)

async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    type_annotation_map = {
        dict[str, Any]: JSON
    }
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    is_banned: Mapped[bool] = mapped_column(default=False)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def ping_db() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        return True
    except:
        return False


def connection(method: Callable) -> Callable:
    async def wrapper(*args, **kwargs) -> Any:
        async with async_session() as session:
            try:
                if 'session' not in kwargs:
                    kwargs['session'] = session
                result = await method(*args, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e

    return wrapper
