import asyncio

from redis.asyncio.client import Redis

from module.ai_module import ai_module_tasks

redis = None


async def init_redis():
    try:
        global redis
        # 일반 테스트용
        redis = Redis(host='localhost', port=6379, decode_responses=True)
        # docker swarm 테스트용
        # return Redis(host='redis_service', port=6379, db=0)

        if redis is None:
            print('Redis is not connected')
        else:
            print('Redis is connected')
    except Exception as e:
        print(e)


async def get_redis():
    try:
        global redis
        if redis is not None:
            yield redis
    finally:
        if redis:
            await redis.close()


async def redis_listener():
    try:
        global redis
        pubsub = redis.pubsub()
        await pubsub.subscribe('AI_MODULE_ORDER')

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                print(f"수신 데이터: {message['data']}")
                datas = message['data'].split(':')
                id = int(datas[1])
                status = datas[2]
                task = ai_module_tasks.get(id)
                if task is not None:
                    if status == 'STOP':
                        task.cancel()
                        ai_module_tasks.pop(id, None)
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f'Listener error: {e}')
    finally:
        await pubsub.unsubscribe('AI_MODULE_ORDER')
        await pubsub.close()
