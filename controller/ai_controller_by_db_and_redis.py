import asyncio
import functools

from fastapi import APIRouter, status as res_status, Depends, Body, HTTPException, Query, Path
from redis.asyncio.client import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.AIModuleRequest import AIModuleRequest
from domain.AIModuleResponse import AIModuleResponse
from model.enums import StatusType
from model.models import AI_Module
from module.ai_module import ai_module, ai_module_callback, ai_module_tasks
from util.init_database import get_db
from util.init_redis import get_redis

# http://localhost:8000/api/ai
router = APIRouter(prefix='/ai')


# SQLAlchemy 2.0v


# http://localhost:8000/api/ai
@router.get('')
async def find_all(
        db: AsyncSession = Depends(get_db)
):
    rs = await db.execute(select(AI_Module).order_by(AI_Module.id.asc()))
    find_ai_modules = rs.scalars().all()
    return [AIModuleResponse.model_validate(ai) for ai in find_ai_modules]


# http://localhost:8000/api/ai?id={id}
# http://localhost:8000/api/ai?id=1
@router.get('/{id}')
async def find_one(
        id: int = Path(...),
        db: AsyncSession = Depends(get_db)
):
    # 1-1.Native Query
    # query = text('SELECT * FROM module AS ai where ai.id = :id ORDER BY ai.id ASC')
    # result = await db.execute(query, {'id': id})
    # find_ai_module = result.fetchone()

    # 1-2.ORM
    rs = await db.execute(select(AI_Module).where(AI_Module.id == id).order_by(AI_Module.id.asc()))
    find_ai_module = rs.scalar_one_or_none()

    if find_ai_module is None:
        raise HTTPException(status_code=404, detail=f'{id}번 모듈이 없습니다')
    return AIModuleResponse.model_validate(find_ai_module)


# http://localhost:8000/api/ai
@router.post('')
async def create(
        name: str = Body(...),
        version: str = Body(...),
        db: AsyncSession = Depends(get_db)
):
    # 1-1.Insert - value 방식
    # query = insert(AI_Module).values(name=name, version=version).returning(AI_Module)
    # result = await db.execute(query)
    # module = result.scalar_one()
    # await db.commit()

    # 1-2.간편 방식
    new_ai_module = AI_Module(name=name, version=version)
    db.add(new_ai_module)
    await db.commit()
    await db.refresh(new_ai_module)
    return AIModuleResponse.model_validate(new_ai_module)


# http://localhost:8000/api/ai/{id}
# http://localhost:8000/api/ai/1
@router.put('/{id}')
async def modify(
        id: int,
        # name: str = Body(...),
        # version: str = Body(...),
        ai_module_request: AIModuleRequest,
        db: AsyncSession = Depends(get_db)
):
    rs = await db.execute(select(AI_Module).where(AI_Module.id == id))
    find_ai_module = rs.scalar_one_or_none()
    if find_ai_module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 없습니다')

    find_ai_module.name = ai_module_request.name
    find_ai_module.version = ai_module_request.version
    await db.commit()
    await db.refresh(find_ai_module)
    return AIModuleResponse.model_validate(find_ai_module)


# http://localhost:8000/api/ai?id={id}
# http://localhost:8000/api/ai?id=1
@router.delete('')
async def delete(
        id: int = Query(...),
        db: AsyncSession = Depends(get_db)
):
    rs = await db.execute(select(AI_Module).where(AI_Module.id == id))
    find_ai_module = rs.scalar_one_or_none()
    if find_ai_module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 없습니다')
    await db.delete(find_ai_module)
    await db.commit()

    return AIModuleResponse.model_validate(find_ai_module)


@router.get('/start/{id}')
async def start(
        id: int = Path(...),
        db: AsyncSession = Depends(get_db)
):
    # 모듈 조회
    rs = await db.execute(select(AI_Module).filter(AI_Module.id == id))
    find_module = rs.scalar_one_or_none()
    if find_module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 없습니다')
    name = find_module.name
    status = find_module.status

    # STOP 상태는 모든 서버의 ai_module_tasks에 해당 id의 task가 모두 없는 상태
    if status == StatusType.STOP:
        task = asyncio.create_task(ai_module(id, name))
        task.add_done_callback(functools.partial(ai_module_callback, module=find_module))
        ai_module_tasks[id] = task
        find_module.status = StatusType.START
        await db.commit()
        await db.refresh(find_module)

    return f'{id}번 {name} 모듈 구동'


@router.get('/stop/{id}')
async def stop(
        id: int,
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis)
):
    rs = await db.execute(select(AI_Module).filter(AI_Module.id == id))
    find_module = rs.scalar_one_or_none()
    if find_module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 없습니다')
    name = find_module.name
    status = find_module.status

    # START 상태는 모든 서버 중 하나만 ai_module_tasks에 해당 id의 task가 존재하는 상태
    if status == StatusType.START:
        await redis.publish(f'AI_MODULE_ORDER', f'AI_MODULE:{id}:STOP')
        find_module.status = StatusType.STOP
        await db.commit()
        await db.refresh(find_module)

    return f'{id}번 {name} 모듈 정지'
