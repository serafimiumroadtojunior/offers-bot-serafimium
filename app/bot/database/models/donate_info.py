from datetime import timedelta

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    BigInteger, Integer, 
    String, DateTime,
    UniqueConstraint,
    PrimaryKeyConstraint
)

from ..session import Base


class UserChecks(Base):
    __tablename__ = "donate_checks"
    __table_args__ = (
        PrimaryKeyConstraint(
            'id',
            name='primary_key_id'
        ),
        UniqueConstraint(
            'check_id',
            name='uq_check_id'
        ),
        UniqueConstraint(
            'charge_id',
            name='uq_charge_id'
        )
    )

    id: Mapped[int] = mapped_column(
    Integer, 
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        index=True
    )
    check_id: Mapped[str] = mapped_column(
        String(10)
    )
    charge_id: Mapped[str] = mapped_column(
        String(100)
    )
    stars_amount: Mapped[int] = mapped_column(
        Integer
    )
    deleted_at: Mapped[timedelta] = mapped_column(
        DateTime, 
        default=timedelta(
            days=7
        )
    )