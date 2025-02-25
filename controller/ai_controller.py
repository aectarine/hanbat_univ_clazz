import asyncio

from fastapi import APIRouter, Body, status as res_status, HTTPException

router = APIRouter(prefix='/ai')

module_list = list()


@router.get('', status_code=res_status.HTTP_200_OK)
async def find_all_ai():
    return [{'name': ai['name'], 'version': ai['version'], 'status': ai['status']} for ai in module_list]


@router.post('')
async def create_ai(
        name: str = Body(...),
        version: str = Body(...),
        status: str = Body(...)
):
    ai = {
        'name': name,
        'version': version,
        'status': status
    }
    module_list.append(ai)
    return module_list


@router.put('', status_code=200)
async def modify_ai(
        name: str = Body(...),
        version: str = Body(...),
        status: str = Body(...)
):
    for ai in module_list:
        if ai['name'] == name:
            ai['version'] = version
            ai['status'] = status

    return module_list


@router.delete('/{name}')
async def remove_ai(
        name: str
):
    for ai in module_list:
        if ai['name'] == name:
            module_list.remove(ai)
    return module_list


@router.post('/start')
async def start_ai_module(
        name: str = Body(..., embed=True)
):
    for ai in module_list:
        if ai['name'] == name:
            ai['task'] = asyncio.create_task(ai_module(name))
            ai['task'].add_done_callback(callback)
            ai['status'] = 'START'
    return f'{name} 모듈 구동 시작'


async def ai_module(name: str):
    print(f'{name} 모듈 구동중...')
    for i in range(0, 100000000000000):
        if i % 10000000 == 0:
            print('1000000000')
        await asyncio.sleep(0)
    print(f'{name} 모듈 구동 완료...')
    # while True:
    #     print(f'{name} 모듈 구동중...')
    #     await asyncio.sleep(1)


def callback(task):
    try:
        print(f'태스크 {task.get_name()}이(가) 완료됨')
        print(f'결과: {task.result()}')
    except asyncio.CancelledError:
        print(f'태스크가 취소되었습니다')
    except Exception as e:
        print(f'오류 발생: {e}')


@router.post('/stop')
async def stop_ai_module(
        name: str = Body(..., embed=True)
):
    for ai in module_list:
        if ai['name'] == name:
            ai['task'].cancel()
            ai['status'] = 'STOP'
            await asyncio.sleep(0.1)
    return f'{name} 모듈 구동 시작'


@router.get('/tasks')
async def get_all_tasks():
    current_tasks = asyncio.all_tasks()
    for task in current_tasks:
        print(task)
    return [{'name': task.get_name(), 'done': task.done(), 'cancelled': task.cancelled(), 'state': str(task._state)} for task in current_tasks]
