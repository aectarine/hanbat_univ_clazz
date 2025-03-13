import asyncio
import functools

from fastapi import APIRouter, status as res_status, Depends, Body, HTTPException, Query, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.AIModuleRequest import AIModuleRequest
from domain.AIModuleResponse import AIModuleResponse
from model.enums import StatusType
from model.models import AI_Module
from util.init_database import get_db

# http://localhost:8000/api/ai
router = APIRouter(prefix='/ai')

running_tasks = {}


# SQLAlchemy 2.0v


# http://localhost:8000/api/ai
@router.get('')
async def find_all(
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AI_Module).order_by(AI_Module.id.asc()))
    find_ai_modules = result.scalars().all()
    return [AIModuleResponse.model_validate(ai) for ai in find_ai_modules]


# http://localhost:8000/api/ai?id={id}
# http://localhost:8000/api/ai?id=1
@router.get('/{id}')
async def find_one(
        id: int = Path(...),
        db: AsyncSession = Depends(get_db)
):
    # 1.Native Query
    # query = text('SELECT * FROM module AS ai where ai.id = :id ORDER BY ai.id ASC')
    # result = await db.execute(query, {'id': id})
    # find_ai_module = result.fetchone()

    # 2.ORM
    result = await db.execute(select(AI_Module).where(AI_Module.id == id).order_by(AI_Module.id.asc()))
    find_ai_module = result.scalar_one_or_none()
    return AIModuleResponse.model_validate(find_ai_module)


# http://localhost:8000/api/ai
@router.post('')
async def create(
        name: str = Body(...),
        version: str = Body(...),
        db: AsyncSession = Depends(get_db)
):
    # 1.Insert - value 방식
    # query = insert(AI_Module).values(name=name, version=version).returning(AI_Module)
    # result = await db.execute(query)
    # module = result.scalar_one()
    # await db.commit()

    # 2.간편 방식
    ai_module = AI_Module(name=name, version=version)
    db.add(ai_module)
    await db.commit()
    await db.refresh(ai_module)
    return AIModuleResponse.model_validate(ai_module)


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
    result = await db.execute(select(AI_Module).where(AI_Module.id == id))
    find_ai_module = result.scalar_one_or_none()
    if find_ai_module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND)

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
    result = await db.execute(select(AI_Module).where(AI_Module.id == id))
    find_ai_module = result.scalar_one_or_none()
    if find_ai_module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND)
    await db.delete(find_ai_module)
    await db.commit()
    return AIModuleResponse.model_validate(find_ai_module)


async def ai_module(id: int, name: str):
    print(f'===> {id}번 {name} 모듈 구동 시작...')
    for i in range(0, 1000000000):  # 숫자를 줄여서 예시
        if i % 1000000 == 0:
            print(f'===> {id}번 {name} 모듈 구동중...')
        await asyncio.sleep(0)  # I/O 대기 중에 CPU를 풀어줌
    print(f'===> {id}번 {name} 모듈 구동 완료...')


def callback(task, module):
    try:
        result = task.result()
        print(f'===> {module.id}번 {module.name} 모듈 완료')
        print(f'===> 결과: {result}')
    except asyncio.CancelledError:
        print(f'===> {module.id}번 {module.name} 모듈 정지됨')
    except Exception as e:
        print(f'===> {module.id}번 {module.name} 모듈 오류 발생: {e}')


@router.get('/start/{id}')
async def start(
        id: int = Path(...),
        db: AsyncSession = Depends(get_db)
):
    # 모듈 조회
    result = await db.execute(select(AI_Module).filter(AI_Module.id == id))
    find_module = result.scalar_one_or_none()
    if find_module is None:
        return f'{id}번 {find_module.name} 모듈이 없습니다'

    # 모듈 구동
    name = find_module.name
    task = asyncio.create_task(ai_module(id, name))
    task.add_done_callback(functools.partial(callback, module=find_module))
    running_tasks[id] = task
    find_module.status = StatusType.START
    await db.commit()
    await db.refresh(find_module)
    return f'{id}번 {name} 모듈 구동'


@router.get('/stop/{id}')
async def stop(
        id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AI_Module).filter(AI_Module.id == id))
    find_module = result.scalar_one_or_none()
    if find_module is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 존재하지 않습니다')

    task = running_tasks.get(id)
    if task is None:
        raise HTTPException(status_code=res_status.HTTP_404_NOT_FOUND, detail=f'{id}번 모듈이 실행 중이지 않습니다')

    task.cancel()
    running_tasks.pop(id, None)

    find_module.status = StatusType.STOP
    name = find_module.name
    await db.commit()
    await db.refresh(find_module)

    return f'{id}번 {name} 모듈 정지'
