from contextlib import asynccontextmanager

from redis.asyncio.client import Redis


@asynccontextmanager
async def get_redis():
    # 일반 테스트용
    redis = Redis(host='localhost', port=6379)
    # docker swarm 테스트용
    # return Redis(host='redis_service', port=6379, db=0)
    try:
        yield redis
    finally:
        if redis:
            await redis.close()
