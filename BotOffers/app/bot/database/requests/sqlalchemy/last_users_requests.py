from typing import Optional, Tuple, Sequence, List

from sqlalchemy import Result
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert

from app.bot.keyboards import SendUserCallback
from app.bot.database.models import LateUsers
from app.bot.database.session import async_session


async def add_late_user(
    user_id: int,
    full_name: str
) -> None:
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                insert(LateUsers)
                .values(
                    user_id=user_id,
                    full_name=full_name
                )
            )


async def get_late_user() -> Optional[Tuple[List[str], List[str]]]:
    late_users_callbacks: List[str] = []
    late_users_buttons: List[str] = []

    async with async_session() as session:  
        async with session.begin():
            result: Result[Tuple[LateUsers]] = await session.execute(
                select(LateUsers)
                .order_by(LateUsers.created_at.desc())
                .limit(5)
            )

            if not result:
                return None

            last_users: Sequence[LateUsers] = result.scalars().all()

            for user in last_users:
                late_users_callbacks.append(
                    SendUserCallback(
                        user_id=user.user_id,
                        full_name=user.full_name
                    ).pack()
                )

                late_users_buttons.append(
                    f"<i>{user.full_name}[{user.user_id}]</i>"
                )

            return late_users_buttons, late_users_callbacks