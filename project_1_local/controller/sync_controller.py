import asyncio
import time

from fastapi import APIRouter

sync_router = APIRouter()


def sync_func_1():
    for i in range(0, 10):
        print(f'sync_func_1-{i}')
        time.sleep(1)


def sync_func_2():
    for i in range(0, 10):
        print(f'sync_func_2-{i}')
        time.sleep(1)


# 동기 함수는 쓰레드 풀에서 관리하고, 하나의 쓰레드 할당
@sync_router.get('/sync')
def t1():
    sync_func_1()
    sync_func_2()
    print('sync 함수 끝')
    return True


async def async_func_1():
    for i in range(0, 10):
        print(f'async_func_1-{i}')
        await asyncio.sleep(1)


async def async_func_2():
    for i in range(0, 10):
        print(f'async_func_2-{i}')
        await asyncio.sleep(1)


# 비동기 함수는 오직 하나의 이벤트 루프에서 async def로 실행된 코루틴 함수를 수행
@sync_router.get('/async')
async def t2():
    await async_func_1()
    await async_func_2()
    # await asyncio.gather(async_func_1(), async_func_2())
    # asyncio.create_task(async_func_1())
    # asyncio.create_task(async_func_2())
    print('async 함수 끝')
    return True
