from sqlalchemy.ext.asyncio import AsyncSession

from app.database import connection, User


class UserDAO:
    @classmethod
    @connection
    async def ban(cls, user_id: int, session: AsyncSession) -> None:
        user = await session.get(User, user_id)
        if user is None:
            user = User(id=user_id, is_banned=True)
            session.add(user)
        else:
            user.is_banned = True

    @classmethod
    @connection
    async def unban(cls, user_id: int, session: AsyncSession) -> None:
        user = await session.get(User, user_id)
        if user is not None:
            user.is_banned = False

    @classmethod
    @connection
    async def is_banned(cls, user_id: int, session: AsyncSession) -> bool:
        user = await session.get(User, user_id)
        if user is not None:
            return bool(user.is_banned)
        return False
