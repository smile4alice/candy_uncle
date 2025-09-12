from aiogram.fsm.storage.redis import Redis, RedisStorage

from app.config import settings


redis_engine = Redis(
    host=settings.REDIS_HOST,
    password=settings.REDIS_PASSWORD,
    port=settings.REDIS_PORT,
)

redis_storage = RedisStorage(redis=redis_engine)
