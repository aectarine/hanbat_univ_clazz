import asyncio
import functools
import uuid

from fastapi import APIRouter, Body, status as res_status

router = APIRouter(prefix='/ai')

module_list = list()


@router.get('', status_code=res_status.HTTP_200_OK)
async def find_all():
    result = [
        {'id': module['id'], 'name': module['name'], 'version': module['version'], 'status': module['status']} for module in module_list
    ]
    return result


@router.get('/{id}', status_code=res_status.HTTP_200_OK)
async def find_one(id: str):
    for module in module_list:
        if module['id'] == id:
            return {'id': module['id'], 'name': module['name'], 'version': module['version'], 'status': module['status']}


@router.post('', status_code=res_status.HTTP_201_CREATED)
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
    }
    module_list.append(module)
    return module_list


@router.put('/{id}', status_code=res_status.HTTP_200_OK)
async def modify(
        id: str,
        name: str = Body(...),
        version: str = Body(...)
):
    for ai in module_list:
        if ai['id'] == id:
            ai['name'] = name
            ai['version'] = version
    return module_list


@router.delete('/{id}', status_code=res_status.HTTP_200_OK)
async def remove(id: str):
    for ai in module_list:
        if ai['id'] == id:
            module_list.remove(ai)
    return module_list


async def ai_module(name: str):
    print(f'{name} 모듈 구동 시작...')
    for i in range(0, 100000000000000):
        if i % 1000000 == 0:
            print(f'{name} 모듈 구동중...')
        await asyncio.sleep(0)
    print(f'{name} 모듈 구동 완료...')


def callback(task, module):
    try:
        result = task.result()  # task.result()를 사용하여 결과를 얻습니다.
        print(f'모듈 {module["name"]}이(가) 완료되었습니다')
        print(f'결과: {result}')
    except asyncio.CancelledError:
        print(f'모듈 {module["name"]}이(가) 정지되었습니다')
    except Exception as e:
        print(f'모듈 {module["name"]}이(가) 오류가 발생했습니다: {e}')


@router.get('/start/{id}', status_code=res_status.HTTP_200_OK)
async def start(id: str):
    for module in module_list:
        if module['id'] == id and module['status'] == 'STOP':
            name = module['name']
            task = asyncio.create_task(ai_module(name))
            task.add_done_callback(functools.partial(callback, module=module))
            module['task'] = task
            module['status'] = 'START'
            return f'{id} 모듈 구동'
    return f'{id} 모듈 구동 실패'


@router.get('/stop/{id}', status_code=res_status.HTTP_200_OK)
async def stop(id: str):
    for module in module_list:
        if module['id'] == id and module['status'] == 'START':
            module['task'].cancel()
            module['status'] = 'STOP'
            await asyncio.sleep(0)
            return f'{id} 모듈 정지'
    return f'{id} 모듈 정지 실패'
