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
        print(f'Redis 연결 오류: {e}')
        redis = None


async def get_redis():
    global redis
    if redis is None:
        await init_redis()
    if redis is not None:
        yield redis


async def redis_listener():
    """Redis Pub/Sub 리스너"""
    while True:
        try:
            global redis
            if redis is None:
                await init_redis()
            if redis is None:
                print('Redis 재연결 실패')
                await asyncio.sleep(5)  # 5초 후 재시도
                continue

            pubsub = redis.pubsub()
            await pubsub.subscribe('AI_MODULE')

            print("Redis 리스너 실행 중...")
            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
                if msg:
                    print(f'수신 데이터: {msg}')
                    datas = msg['data'].split(':')
                    id = int(datas[0])
                    status = datas[1]
                    task = ai_module_tasks.get(id)
                    if task is not None and status == StatusType.STOP.value:
                        task.cancel()
                        ai_module_tasks.pop(id, None)

        except Exception as e:
            print(f'Redis 리스너 오류 발생: {e}')
        finally:
            if redis:
                await pubsub.unsubscribe('AI_MODULE')
                await pubsub.close()
                redis = None  # 연결이 끊기면 다시 연결하도록 설정
            await asyncio.sleep(5)  # 5초 후 재연결 시도
