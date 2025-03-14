import asyncio

ai_module_tasks = {}


async def ai_module(id: int, name: str):
    print(f'===> {id}번 {name} 모듈 구동 시작...')
    for i in range(0, 1000000000):  # 숫자를 줄여서 예시
        if i % 1000000 == 0:
            print(f'===> {id}번 {name} 모듈 구동 중...')
        await asyncio.sleep(0)  # I/O 대기 중에 CPU를 풀어줌
    print(f'===> {id}번 {name} 모듈 구동 완료...')


def ai_module_callback(task, module):
    try:
        result = task.result()
        print(f'===> {module.id}번 {module.name} 모듈 완료')
        print(f'===> 결과: {result}')
    except asyncio.CancelledError:
        print(f'===> {module.id}번 {module.name} 모듈 정지됨')
    except Exception as e:
        print(f'===> {module.id}번 {module.name} 모듈 오류 발생: {e}')
