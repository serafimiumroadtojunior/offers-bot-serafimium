from typing import Optional, Tuple, Union
from datetime import timedelta, datetime, timedelta

from sqlalchemy import Result, delete
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from aiogram_i18n import I18nContext

from app.bot.database.models import UserChecks
from app.bot.database.session import async_session


async def add_user_check(
    user_id: int,
    stars_amount: int,
    charge_id: str,
    check_id: str
) -> None:
    async with async_session() as session:
        async with session.begin():
            checker_id: Result[Tuple[str]] = await session.execute(
                insert(UserChecks)
                .values(
                    user_id=user_id,
                    stars_amount=stars_amount,
                    check_id=check_id,
                    charge_id=charge_id
                )
                .on_conflict_do_nothing(
                    index_elements=[UserChecks.check_id]
                ).returning(UserChecks.check_id)
            )

            if not checker_id:
                await add_user_check(
                    user_id=user_id,
                    stars_amount=stars_amount,
                    check_id=check_id,
                    charge_id=charge_id
                )

                return None


async def get_user_check(
    check_id: str,
    locale: str,
    i18n: I18nContext
) -> Optional[Tuple[str, int, str, str]]:
    async with async_session() as session:
        async with session.begin():
            result: Result[Tuple[UserChecks]] = await session.execute(
                select(UserChecks)
                .where(UserChecks.check_id == check_id)
            )

            payment_element: Optional[UserChecks] = result.scalar()

            if not payment_element:
                return None
            
            payment_code: str = payment_element.check_id
            payment_charge: str = payment_element.charge_id
            payment_amount: int = payment_element.stars_amount
            payment_data: timedelta = payment_element.deleted_at
            status: str = i18n.get(
                "succes-status",
                locale
            )

            if payment_data < timedelta():
                status: str = i18n.get(
                    "error-time-life",
                    locale
                )

            return payment_charge, payment_amount, status, payment_code
        

async def refund_delete_check(
    charge_id: str
) -> None:
    async with async_session() as session:
        async with session.begin():
            await session.execute(
            delete(UserChecks)
            .where(UserChecks.charge_id == charge_id)
        )