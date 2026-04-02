import redis.asyncio as aioredis

import os
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

redis_client : Optional[aioredis.Redis] = None

async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    return redis_client


async def cache_get(key: str) -> Optional[Any]:
    try:
        client = await get_redis()
        value = await client.get(key)
        if value is not None:
            return json.loads(value)
    except Exception as e:
        logger.warning(f"Redis GET failed for key {key}: {e}")
    return None

async def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    try:
        client = await get_redis()
        await client.set(key, json.dumps(value, default=str), ex=ttl)
        return True
    except Exception as e:
        logger.warning(f"Redis SET failed for key {key}: {e}")
    return False

async def cache_delete(key: str) -> bool:
    try:
        client = await get_redis()
        await client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Redis DELETE failed for key {key}: {e}")
    return False

async def cache_delete_pattern(pattern: str) -> int:
    try:
        client = await get_redis()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
            return len(keys)
        return 0
    except Exception as e:
        logger.warning(f"Redis DELETE failed for pattern {pattern}: {e}")
    return 0