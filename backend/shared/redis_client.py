import redis
from backend.shared.config import shared_config

redis_client = redis.Redis(
    host=shared_config.REDIS_HOST,
    port=shared_config.REDIS_PORT,
    db=0,
    decode_responses=True
)