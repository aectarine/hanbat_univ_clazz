import asyncio
import functools
from asyncio import sleep

from fastapi import APIRouter, status as res_status, Depends, Body, HTTPException, Query
from redis.asyncio.client import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.AIModuleResponse import AIModuleResponse
from model.enums import StatusType
from model.models import AI_Module
from util.init_database import get_db
from util.init_redis import get_redis

router = APIRouter(prefix='/ai')
running_tasks = {}


async def run_ai_module(id: int):
    while await is_task_running(id):
        print(f'{id}번 모듈 구동 시작...')
        for i in range(0, 10000000000000):
            if i % 1000000 == 0:
                print(f'{id}번 모듈 구동중...')
            await sleep(0)
        print(f'{id}번 모듈 구동 완료...')


def task_callback(task, module):
    try:
        task.result()
        print(f'모듈 {module.name} 완료')
    except asyncio.CancelledError:
        print(f'모듈 {module.name} 정지됨')
    except Exception as e:
        print(f'모듈 {module.name} 오류: {e}')


# Routes
@router.get('')
async def get_all_modules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AI_Module).order_by(AI_Module.id.asc()))
    modules = result.scalars().all()
    return [AIModuleResponse.model_validate(module) for module in modules]


@router.get('/{id}')
async def get_module(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AI_Module).where(AI_Module.id == id))
    module = result.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail="Module not found")
    return AIModuleResponse.model_validate(module)


@router.post('')
async def create_module(name: str = Body(...), version: str = Body(...), db: AsyncSession = Depends(get_db)):
    ai_module = AI_Module(name=name, version=version)
    db.add(ai_module)
    await db.commit()
    await db.refresh(ai_module)
    return AIModuleResponse.model_validate(ai_module)


@router.put('/{id}')
async def update_module(id: int, name: str = Body(...), version: str = Body(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AI_Module).where(AI_Module.id == id))
    module = result.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail="Module not found")
    module.name = name
    module.version = version
    await db.commit()
    await db.refresh(module)
    return AIModuleResponse.model_validate(module)


@router.delete('')
async def delete_module(id: int = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AI_Module).where(AI_Module.id == id))
    module = result.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail="Module not found")
    await db.delete(module)
    await db.commit()
    return AIModuleResponse.model_validate(module)


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


async def task_listener() -> None:
    async with get_redis() as redis:
        pubsub = redis.pubsub()
        await pubsub.subscribe('ai_module')

        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    action, task_id = message['data'].decode().split(':')
                    task_id = int(task_id)

                    if action == 'start':
                        task = asyncio.create_task(run_ai_module(task_id))
                        running_tasks[task_id] = task
                    elif action == 'stop':
                        task = running_tasks.get(task_id)
                        if task:
                            task.cancel()
                            running_tasks.pop(task_id, None)

        except asyncio.CancelledError:
            # task_listener가 취소될 때 처리
            print("task_listener가 취소되었습니다")

        finally:
            # Pub/Sub 연결을 종료
            await pubsub.unsubscribe('ai_module')
            await pubsub.close()


@router.get('/start/{id}')
async def start_module(id: int, redis: Redis = Depends(get_redis), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AI_Module).where(AI_Module.id == id))
    module = result.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail="Module not found")

    await save_task(id)
    async with redis as r:
        await r.publish('ai_module', f'start:{id}')

    task = asyncio.create_task(run_ai_module(id))
    task.add_done_callback(functools.partial(task_callback, module=module))
    running_tasks[id] = task
    module.status = StatusType.START
    await db.commit()
    await db.refresh(module)

    return f'{id}번 모듈 구동 시작'


@router.get('/stop/{id}')
async def stop_module(id: int, redis: Redis = Depends(get_redis), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AI_Module).where(AI_Module.id == id))
    module = result.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail="Module not found")

    task = running_tasks.get(id)
    if task:
        task.cancel()
        running_tasks.pop(id, None)

    await remove_task(id)
    async with redis as r:
        await r.publish('ai_module', f'stop:{id}')

    await db.commit()
    await db.refresh(module)

    return f'{id}번 모듈이 정지되었습니다'
