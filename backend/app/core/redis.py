import redis
from app.core.config import settings

# CLIENT
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)

def check_redis_connection() -> bool:
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False