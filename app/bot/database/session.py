from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncAttrs, AsyncEngine, AsyncSession,
    async_sessionmaker, create_async_engine
)

from app.bot.settings import Settings


settings: Settings = Settings()
engine: AsyncEngine = create_async_engine(url=settings.psql_dsn())
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass