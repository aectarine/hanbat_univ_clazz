import asyncio
from asyncio import sleep, gather
from time import sleep as t_sleep

from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix='/test')


async def one_to_ten(num):
    for i in range(0, num):
        print(f'{num}-{i}')
        await sleep(1)
    return num


def one_to_ten2(num):
    for i in range(0, num):
        print(f'{num}-{i}')
        t_sleep(1)
    return num


@router.get('/t1')
def sync_test1():
    one_to_ten2(10)
    one_to_ten2(20)
    return 'end'


@router.get('/t2')
async def async_test2():
    await one_to_ten(10)
    await one_to_ten(20)
    return 'end'


@router.get('/t3')
async def async_test3():
    await gather(one_to_ten(10), one_to_ten(20))
    return 'end'


def callback(task):
    print(f'태스크 {task.get_name()}이(가) 완료')
    print(f'결과: {task.result()}')


@router.get('/t4')
async def async_test4():
    task_1 = asyncio.create_task(one_to_ten(10))
    task_2 = asyncio.create_task(one_to_ten(20))
    task_1.add_done_callback(callback)
    task_2.add_done_callback(callback)
    return 'end'


@router.get('/t5')
async def async_test5(background_task: BackgroundTasks):
    async def gather_tasks():
        await gather(one_to_ten(10), one_to_ten(20))
    background_task.add_task(gather_tasks)
    return 'end'


@router.get('/t6')
async def async_test6():
    all_tasks = asyncio.all_tasks()
    print(all_tasks)
    return 'end'
