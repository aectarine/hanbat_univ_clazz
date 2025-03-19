import asyncio
import functools
import uuid
from datetime import datetime

from fastapi import APIRouter, Body, Query

from module.ai_module import ai_module, ai_module_callback

router = APIRouter(prefix='/ai')

module_list = list()


# http://localhost:8000/api/ai
@router.get('')
async def find_all():
    raise Exception('에러!!')
    result = [
        {
            'id': module['id'],
            'name': module['name'],
            'version': module['version'],
            'status': module['status'],
            'inserted': module['inserted'],
            'updated': module['updated']
        } for module in module_list
    ]
    return result


# http://localhost:8000/api/ai/{id}
# http://localhost:8000/api/ai/1
@router.get('/{id}')
async def find_one(id: str):
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


# http://localhost:8000/api/ai
@router.post('')
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


# http://localhost:8000/api/ai/{id}
# http://localhost:8000/api/ai/1
@router.put('/{id}')
async def modify(
        id: str,
        name: str = Body(...),
        version: str = Body(...)
):
    for ai in module_list:
        if ai['id'] == id:
            ai['name'] = name
            ai['version'] = version
            ai['updated'] = datetime.now()
    return module_list


# http://localhost:8000/api/ai?id={id}
# http://localhost:8000/api/ai?id=1
@router.delete('')
async def remove(
        id: str = Query(...)
):
    for ai in module_list:
        if ai['id'] == id:
            module_list.remove(ai)
    return module_list


# http://localhost:8000/api/ai/start/{id}
# http://localhost:8000/api/ai/start/1
@router.get('/start/{id}')
async def start(id: str):
    for module in module_list:
        if module['id'] == id and module['status'] == 'STOP':
            name = module['name']
            task = asyncio.create_task(ai_module(id, name))
            task.add_done_callback(functools.partial(ai_module_callback, id=id, name=name))
            module['task'] = task
            module['status'] = 'START'
            return f'{id} 모듈 구동'
    return f'{id} 모듈 구동 실패'


# http://localhost:8000/api/ai/stop/{id}
# http://localhost:8000/api/ai/stop/1
@router.get('/stop/{id}')
async def stop(id: str):
    for module in module_list:
        if module['id'] == id and module['status'] == 'START':
            module['task'].cancel()
            module['status'] = 'STOP'
            await asyncio.sleep(0)
            return f'{id} 모듈 정지'
    return f'{id} 모듈 정지 실패'
