from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    BigInteger, Integer, 
    DateTime, UniqueConstraint,
    String
)

from ..session import Base


class LateUsers(Base):
    __tablename__ = "late_users"
    __table_args__ = (
        UniqueConstraint(
            'user_id', 
            name='uq_user_id'
        )
    )

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        index=True
    )
    full_name: Mapped[str] = mapped_column(
        String(100)
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, 
        default=datetime.now
    )