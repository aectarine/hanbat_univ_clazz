import asyncio
from contextlib import asynccontextmanager

from redis.asyncio.client import Redis


@asynccontextmanager
async def get_redis():
    try:
        # 일반 테스트용
        redis = Redis(host='localhost', port=6379)
        # docker swarm 테스트용
        # return Redis(host='redis_service', port=6379, db=0)
        yield redis
    finally:
        if redis:
            await redis.close()


@asynccontextmanager
async def redis_listener() -> None:
    async with get_redis() as redis:
        pubsub = redis.pubsub()
        await pubsub.subscribe('module')
        try:
            async for message in pubsub.listen():
                print('Listen: message:', message)
                if message['type'] == 'message':
                    action, task_id = message['data'].decode().split(':')
                    task_id = int(task_id)
                    if action == 'start':
                        print('@@@ START @@@')
                        task = asyncio.create_task(ai_module(task_id))
                        running_tasks[task_id] = task
                    elif action == 'stop':
                        print('@@@ STOP @@@')
                        task = running_tasks.get(task_id)
                        if task:
                            task.cancel()
                            running_tasks.pop(task_id, None)
        except asyncio.CancelledError:
            # redis_listener 취소될 때 처리
            print("redis_listener 취소되었습니다")
        finally:
            # Pub/Sub 연결을 종료
            await pubsub.unsubscribe('module')
            await pubsub.close()


# Helper functions
async def is_task_running(id: int) -> bool:
    async with get_redis() as redis:
        return await redis.exists(f'task:{id}')


async def save_task(id: int) -> None:
    async with get_redis() as redis:
        await redis.set(f'task:{id}', 'running')


async def remove_task(id: int) -> None:
    async with get_redis() as redis:
        await redis.delete(f'task:{id}')


running_tasks = {}


async def ai_module(id: int, name: str):
    while await is_task_running(id):
        print(f'===> {id}번 {name} 모듈 구동 시작...')
        for i in range(0, 1000000000):  # 숫자를 줄여서 예시
            if i % 1000000 == 0:
                print(f'===> {id}번 {name} 모듈 구동 중...')
            await asyncio.sleep(0)  # I/O 대기 중에 CPU를 풀어줌
        print(f'===> {id}번 {name} 모듈 구동 완료...')


def callback(task, module):
    try:
        result = task.result()
        print(f'===> {module.id}번 {module.name} 모듈 완료')
        print(f'===> 결과: {result}')
    except asyncio.CancelledError:
        print(f'===> {module.id}번 {module.name} 모듈 정지됨')
    except Exception as e:
        print(f'===> {module.id}번 {module.name} 모듈 오류 발생: {e}')
