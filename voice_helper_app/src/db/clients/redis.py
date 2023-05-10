from aioredis import (ConnectionPool,
                      Redis)

from core.configs import settings

redis_message_host = settings.redis_message_host
redis_message_port = settings.redis_message_port

redis_message: Redis | None = None


def create_redis_message():
    pool = ConnectionPool.from_url(f"redis://{redis_message_host}:{redis_message_port}", max_connections=10)
    redis = Redis(connection_pool=pool)
    return redis


def get_redis_message():
    return redis_message
