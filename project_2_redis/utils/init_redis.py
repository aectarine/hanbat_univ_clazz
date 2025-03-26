import asyncio

from redis.asyncio.client import Redis

from project_2_redis.model.enums import StatusType
from project_2_redis.module.ai_module import ai_module_tasks

redis = None


async def init_redis():
    try:
        global redis
        redis = Redis(host='localhost', port=6379, decode_responses=True)

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
        pubsub = redis.pubsub()
        await pubsub.subscribe('AI_MODULE')

        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if msg:
                print(f'수신 데이터: {msg}')
                datas = msg['data'].split(':')
                id = int(datas[0])
                status = datas[1]
                task = ai_module_tasks.get(id)
                if task is not None:
                    if status == StatusType.STOP.value:
                        task.cancel()
                        ai_module_tasks.pop(id, None)
    except Exception as e:
        print(f'Redis 리스너 오류 발생: {e}')
    finally:
        await pubsub.unsubscribe('AI_MODULE')
        await pubsub.close()
