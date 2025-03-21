from redis.asyncio.client import Redis

redis = None


async def init_redis():
    try:
        global redis
        redis = Redis(host='0.0.0.0', port=6379, decode_responses=True)

        if await redis.ping():
            print('Redis 연결 완료')
        else:
            print('Redis 연결 실패')
            raise Exception('Redis 연결 실패')
    except Exception as e:
        print(e)


async def get_redis():
    try:
        global redis
        if redis:
            yield redis
    except Exception as e:
        print(f'Redis 연결중 오류 발생: {e}')
        raise
    finally:
        if redis:
            await redis.close()


async def redis_listener():
    try:
        global redis
    except Exception as e:
        print(f'Redis 리스너 오류 발생: {e}')
