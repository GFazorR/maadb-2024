import aioredis

redis_url = "redis://redis:6379"  # Adjust based on your Redis service name in docker-compose
redis_pool = None


async def get_redis_pool():
    global redis_pool
    if redis_pool is None:
        redis_pool = await aioredis.create_redis_pool(redis_url)
    return redis_pool
