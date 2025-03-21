import asyncio
import functools
import uuid
from datetime import datetime

from fastapi import APIRouter, Path, Body, Depends, HTTPException, status as res_status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project_1_local.module.ai_module import ai_module_callback
from project_2_redis.domain.ai_module_request import AIModuleRequest
from project_2_redis.domain.ai_module_response import AIModuleResponse
from project_2_redis.model.models import AI_Module
from project_2_redis.module.ai_module import ai_module
from project_2_redis.utils.init_db import get_db

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
        id: str = Path(...),
        db: AsyncSession = Depends(get_db)
):
    module = await db.execute(select(AI_Module).where(AI_Module.id == id).order_by(AI_Module.id.asc()))
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


# 4. 모듈 수정
# PUT http://localhost:8000/api/ai/{id}
@ai_router.put('/{id}')
async def modify(
        id: str = Path(...),
        # name: str = Body(...),
        # version: str = Body(...)
        ai_module_request: AIModuleRequest,
        db: AsyncSession = Depends(get_db)
):
    rs = await db.execute(select(AI_Module).where(AI_Module.id == id))
    module = rs.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 없습니다')
    module.name = ai_module_request.name
    module.version = ai_module_request.version
    await db.commit()
    await db.refresh(module)
    return AIModuleResponse.model_validate(module)


# 5. 모듈 삭제
# DELETE http://localhost:8000/api/ai/{id}
@ai_router.delete('/{id}')
async def delete(
        id: str = Path(...)
):
    for module in module_list:
        if module['id'] == id:
            if module['status'] == 'START':
                try:
                    module['task'].cancel()
                except asyncio.CancelledError:
                    pass
            module_list.remove(module)
    return module_list


# 6. 모듈 구동
# POST http://localhost:8000/api/ai/start/{id}
@ai_router.post('/start/{id}')
async def start(
        id: str = Path(...)
):
    for module in module_list:
        if module['id'] == id and module['status'] == 'STOP':
            name = module['name']
            task = asyncio.create_task(ai_module(id, name))
            task.add_done_callback(functools.partial(ai_module_callback, id=id, name=name))
            module['task'] = task
            module['status'] = 'START'
            module['updated'] = datetime.now()
            return f'{id} 모듈 구동'
    return f'{id} 모듈 구동 실패'


# 7. 모듈 정지
# POST http://localhost:8000/api/ai/stop/{id}
@ai_router.post('/stop/{id}')
async def stop(
        id: str = Path(...)
):
    for module in module_list:
        if module['id'] == id and module['status'] == 'START':
            module['task'].cancel()
            module['status'] = 'STOP'
            module['updated'] = datetime.now()
            return f'{id} 모듈 정지'
    return f'{id} 모듈 정지 실패'
