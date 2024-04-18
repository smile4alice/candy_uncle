from aiogram.fsm.storage.redis import Redis, RedisStorage

from src.config import SETTINGS


redis_engine = Redis(
    host=SETTINGS.REDIS_HOST,
    password=SETTINGS.REDIS_PASSWORD,
    port=SETTINGS.REDIS_PORT,
)

STORAGE = RedisStorage(redis=redis_engine)
