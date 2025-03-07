import asyncio
import functools
from asyncio import sleep

from fastapi import APIRouter, status as res_status, Depends, Body, HTTPException, Query, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.AIModuleResponse import AIModuleResponse
from model.enums import StatusType
from model.models import AI_Module
from util.database import get_db

router = APIRouter(prefix='/ai')

running_tasks = {}


# SQLAlchemy 2.0v


# http://localhost:8001/api/ai
@router.get('')
async def find_all(
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AI_Module))
    find_ai_modules = result.scalars().all()
    return [AIModuleResponse.model_validate(ai) for ai in find_ai_modules]


# http://localhost:8001/api/ai?id={id}
# http://localhost:8001/api/ai?id=1
@router.get('/{id}')
async def find_one(
        id: int = Path(...),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AI_Module).where(AI_Module.id == id))
    find_ai_module = result.scalar_one_or_none()
    return AIModuleResponse.model_validate(find_ai_module)


# http://localhost:8001/api/ai
@router.post('')
async def create(
        name: str = Body(...),
        version: str = Body(...),
        db: AsyncSession = Depends(get_db)
):
    # query = insert(AI_Module).values(name=name, version=version).returning(AI_Module)
    # result = await db.execute(query)
    # ai_module = result.scalar_one()
    # await db.commit()

    ai_module = AI_Module(name=name, version=version)
    db.add(ai_module)
    await db.commit()
    await db.refresh(ai_module)
    return AIModuleResponse.model_validate(ai_module)


# http://localhost:8001/api/ai/{id}
# http://localhost:8001/api/ai/1
@router.put('/{id}')
async def modify(
        id: int,
        name: str = Body(...),
        version: str = Body(...),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AI_Module).where(AI_Module.id == id))
    find_ai_module = result.scalar_one_or_none()
    if find_ai_module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND)
    find_ai_module.name = name
    find_ai_module.version = version
    await db.commit()
    await db.refresh(find_ai_module)
    return AIModuleResponse.model_validate(find_ai_module)


# http://localhost:8001/api/ai?id={id}
# http://localhost:8001/api/ai?id=1
@router.delete('')
async def delete(
        id: int = Query(...),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AI_Module).where(AI_Module.id == id))
    find_ai_module = result.scalar_one_or_none()
    if find_ai_module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND)
    await db.delete(find_ai_module)
    await db.commit()
    return AIModuleResponse.model_validate(find_ai_module)


async def ai_module(name: str):
    print(f'{name} 모듈 구동 시작...')
    for i in range(0, 10000000000000):
        if i % 100000 == 0:
            print(f'{name} 모듈 구동중...')
        await sleep(0)
    print(f'{name} 모듈 구동 완료...')


def callback(task, module):
    try:
        result = task.result()
        print(f'모듈 이(가) 완료되었습니다')
        print(f'결과: {result}')
    except asyncio.CancelledError:
        print(f'모듈 이(가) 정지되었습니다')
    except Exception as e:
        print(f'모듈 이(가) 오류가 발생했습니다: {e}')


@router.get('/start/{id}')
async def start(
        id: int = Path(...),
        db: AsyncSession = Depends(get_db)
):
    # 모듈 조회
    result = await db.execute(select(AI_Module).filter(AI_Module.id == id))
    find_module = result.scalar_one_or_none()
    if find_module is None:
        return f'{id} 모듈이 없습니다'

    # 모듈 구동
    name = find_module.name
    task = asyncio.create_task(ai_module(name))
    task.add_done_callback(functools.partial(callback, module=find_module))
    running_tasks[id] = task
    find_module.status = StatusType.START
    await db.commit()
    await db.refresh(find_module)
    return f'{id}번 {name} 모듈 구동'


@router.get('/stop/{id}')
async def stop(
        id: int,
        db: AsyncSession = Depends(get_db)
):
    # 모듈 조회
    result = await db.execute(select(AI_Module).filter(AI_Module.id == id))
    find_module = result.scalar_one_or_none()
    if find_module is None:
        return f'{id} 모듈이 없습니다'

    # 모듈 정지
    task = running_tasks[id]
    if task is None:
        return f'{id} 모듈이 실행중이지 않습니다'

    task.cancel()
    running_tasks.pop(id, None)

    find_module.status = StatusType.STOP
    await db.commit()
    await db.refresh(find_module)

    return f'{id}번 모듈이 정지되었습니다'
