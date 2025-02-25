import asyncio
import uuid

from fastapi import APIRouter, Body, status as res_status

router = APIRouter(prefix='/ai')

module_list = list()


@router.get('', status_code=res_status.HTTP_200_OK)
async def find_all():
    return [
        {'id': module['id'], 'name': module['name'], 'version': module['version'], 'status': module['status']} for module in module_list
    ]


@router.get('/{id}')
async def find_one(id: str):
    for module in module_list:
        if module['id'] == id:
            return {'id': module['id'], 'name': module['name'], 'version': module['version'], 'status': module['status']}


@router.post('')
async def create(
        name: str = Body(...),
        version: str = Body(...),
        status: str = Body(...)
):
    id = str(uuid.uuid4())
    module = {
        'id': id,
        'name': name,
        'version': version,
        'status': status,
    }
    module_list.append(module)
    return module_list


@router.put('/{id}', status_code=200)
async def modify(
        id: str,
        name: str = Body(...),
        version: str = Body(...),
        status: str = Body(...)
):
    for ai in module_list:
        if ai['id'] == id:
            ai['name'] = name
            ai['version'] = version
            ai['status'] = status
    return module_list


@router.delete('/{id}')
async def remove(
        id: str
):
    for ai in module_list:
        if ai['id'] == id:
            module_list.remove(ai)
    return module_list


async def ai_module(name: str):
    print(f'{name} 모듈 구동 시작...')
    for i in range(0, 100000000000000):
        if i % 10000000 == 0:
            print('구동중...')
        await asyncio.sleep(0)
    print(f'{name} 모듈 구동 완료...')


def callback(task):
    try:
        result = task.result()
        print(f'태스크 {task.get_name()}이(가) 완료됨')
        print(f'결과: {result}')
    except asyncio.CancelledError:
        print(f'태스크 {task.get_name()}이(가) 취소되었습니다')
    except Exception as e:
        print(f'태스크 {task.get_name()}에서 오류 발생: {e}')


@router.get('/start/{id}')
async def start(
        id: str
):
    for ai in module_list:
        if ai['id'] == id and ai['status'] == 'STOP':
            name = ai['name']
            task = asyncio.create_task(ai_module(name))
            task.add_done_callback(callback)
            ai['task'] = task
            ai['status'] = 'START'
            return f'{id} 모듈 구동'
    return f'{id} 모듈 구동 실패'


@router.get('/stop/{id}')
async def stop(
        id: str
):
    for module in module_list:
        if module['id'] == id and module['status'] == 'START':
            module['task'].cancel()
            module['status'] = 'STOP'
            await asyncio.sleep(0)
            return f'{id} 모듈 정지'
    return f'{id} 모듈 정지 실패'
