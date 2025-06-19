from typing import Optional, List

from redis.asyncio import Redis


async def add_user_info(
    user_id: int,
    redis: Redis,
    status: Optional[str] = None,
    user_locale: Optional[str] = None
) -> None:
    user_manager: str = f"user:{user_id}:manager"
    check_info: Optional[List[str]] = await redis.hmget(
        name=user_manager,
        keys=[
            "user_locale",
            "status"
        ]   
    )

    if not check_info:
        return None
    
    if not check_info[0] or not check_info[1]:
        return None

    user_locale: str = check_info[0] if not user_locale else user_locale
    status: str = check_info[1] if not status else status

    await redis.hset(
        name=user_manager,
        mapping={
            "status": status,
            "user_locale": user_locale
        }
    )


async def get_user_locale(
    user_id: int,
    redis: Redis
) -> str:
    user_manager: str = f"user:{user_id}:manager"
    user_locale: Optional[str] = await redis.hget(
        name=user_manager,
        key="user_locale"
    )

    if not user_locale:
        return 'en'
    
    return user_locale
    

async def get_user_status(
    user_id: int,
    redis: Redis
) -> str:
    user_manager: str = f"user:{user_id}:manager"
    user_status: Optional[str] = await redis.hget(
        name=user_manager,
        key="status"
    )

    if not user_status:
        return 'Unbanned'
    
    return user_status