import asyncio
import functools
import uuid
from datetime import datetime

from fastapi import APIRouter, Path, Body

from project_1_local.module.ai_module import ai_module, ai_module_callback

ai_router = APIRouter(prefix='/ai')

module_list = list()


# 1. 모듈 조회
# GET http://localhost:8000/api/ai
@ai_router.get('')
# def find_all(): - API, DB, File 등 I/O 작업이 없거나, await 를 사용하는 비동기 함수가 없는경우 def 사용 가능
async def find_all():
    return [
        {
            'id': module['id'],
            'name': module['name'],
            'version': module['version'],
            'status': module['status'],
            'inserted': module['inserted'],
            'updated': module['updated']
        } for module in module_list
    ]


# 2. 모듈 단일 조회
# GET http://localhost:8000/api/ai/{id}
@ai_router.get('/{id}')
async def find_one(
        id: str = Path(...)
):
    for module in module_list:
        if module['id'] == id:
            return {
                'id': module['id'],
                'name': module['name'],
                'version': module['version'],
                'status': module['status'],
                'inserted': module['inserted'],
                'updated': module['updated']
            }


# 3. 모듈 등록
# POST http://localhost:8000/api/ai
# BODY: name={name}&version={version}
@ai_router.post('')
async def create(
        name: str = Body(...),
        version: str = Body(...)
):
    id = str(uuid.uuid4())
    module = {
        'id': id,
        'name': name,
        'version': version,
        'status': 'STOP',
        'inserted': datetime.now(),
        'updated': datetime.now()
    }
    module_list.append(module)
    return module_list


# 4. 모듈 수정
# PUT http://localhost:8000/api/ai/{id}
@ai_router.put('/{id}')
async def modify(
        id: str = Path(...),
        name: str = Body(...),
        version: str = Body(...)
):
    for module in module_list:
        if module['id'] == id:
            module['name'] = name
            module['version'] = version
            module['updated'] = datetime.now()
    return module_list


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
