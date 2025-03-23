import asyncio
import functools

from fastapi import APIRouter, Path, Depends, HTTPException, status as res_status
from redis.asyncio.client import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project_1_local.module.ai_module import ai_module_callback
from project_2_redis.domain.ai_module_request import AIModuleRequest
from project_2_redis.domain.ai_module_response import AIModuleResponse
from project_2_redis.model.enums import StatusType
from project_2_redis.model.models import AI_Module
from project_2_redis.module.ai_module import ai_module, ai_module_tasks
from project_2_redis.utils.init_db import get_db
from project_2_redis.utils.init_redis import get_redis

ai_router = APIRouter(prefix='/ai')


# 1. 모듈 조회
# GET http://localhost:8000/api/ai
@ai_router.get('')
async def find_all(
        db: AsyncSession = Depends(get_db)
):
    rs = await db.execute(select(AI_Module).order_by(AI_Module.id.asc()))
    module_list = rs.scalars().all()
    return [AIModuleResponse.model_validate(module) for module in module_list]


# 2. 모듈 단일 조회
# GET http://localhost:8000/api/ai/{id}
@ai_router.get('/{id}')
async def find_one(
        id: int = Path(...),
        db: AsyncSession = Depends(get_db)
):
    rs = await db.execute(select(AI_Module).where(AI_Module.id == id).order_by(AI_Module.id.asc()))
    module = rs.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 없습니다')
    return AIModuleResponse.model_validate(module)


# 3. 모듈 등록
# POST http://localhost:8000/api/ai
# BODY: name={name}&version={version}
@ai_router.post('')
async def create(
        # name: str = Body(...),
        # version: str = Body(...)
        ai_module_request: AIModuleRequest,
        db: AsyncSession = Depends(get_db)
):
    name = ai_module_request.name
    version = ai_module_request.version
    module = AI_Module(name=name, version=version)
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return AIModuleResponse.model_validate(module)


@ai_router.put('/{id}')
async def modify(
        id: int = Path(...),
        # name: str = Body(...),
        # version: str = Body(...)
        ai_module_request: AIModuleRequest = None,
        db: AsyncSession = Depends(get_db)
):
    rs = await db.execute(select(AI_Module).where(AI_Module.id == id))
    module = rs.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 없습니다')
    module.name = ai_module_request.name
    module.version = ai_module_request.version
    await db.commit()
    await db.refresh(module)
    return AIModuleResponse.model_validate(module)


# 4. 모듈 수정
# PUT http://localhost:8000/api/ai/{id}


# 5. 모듈 삭제
# DELETE http://localhost:8000/api/ai/{id}
@ai_router.delete('/{id}')
async def delete(
        id: int = Path(...),
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis)
):
    rs = await db.execute(select(AI_Module).where(AI_Module.id == id))
    module = rs.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 없습니다')

    if module.status == StatusType.START:
        await redis.publish(f'AI_MODULE', f'{id}:STOP')
        await db.delete(module)
        await db.commit()
    return AIModuleResponse.model_validate(module)


# 6. 모듈 구동
# POST http://localhost:8000/api/ai/start/{id}
@ai_router.post('/start/{id}')
async def start(
        id: int = Path(...),
        db: AsyncSession = Depends(get_db)
):
    rs = await db.execute(select(AI_Module).where(AI_Module.id == id))
    module = rs.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 없습니다')
    name = module.name

    # STOP 상태는 모든 서버의 ai_module_tasks에 해당 id의 task가 모두 없는 상태
    if module.status == StatusType.STOP:
        task = asyncio.create_task(ai_module(id, name))
        task.add_done_callback(functools.partial(ai_module_callback, id=id, name=name))
        ai_module_tasks[id] = task
        module.status = StatusType.START
        await db.commit()
        return f'{id}번 모듈 구동 성공'
    return f'{id}번 모듈 구동 실패'


# 7. 모듈 정지
# POST http://localhost:8000/api/ai/stop/{id}
@ai_router.post('/stop/{id}')
async def stop(
        id: int = Path(...),
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis)
):
    rs = await db.execute(select(AI_Module).where(AI_Module.id == id))
    module = rs.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 없습니다')

    if module.status == StatusType.START:
        await redis.publish(f'AI_MODULE', f'{id}:STOP')
        module.status = StatusType.STOP
        await db.commit()
        return f'{id}번 모듈 정지 성공'
    return f'{id}번 모듈 정지 실패'
