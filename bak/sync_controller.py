from time import sleep

from fastapi import APIRouter

router = APIRouter(prefix='/sync')


def one_to_ten():
    for i in range(0, 10):
        print(i)
        sleep(1)


@router.get('/t1')
def sync_test():
    one_to_ten()
    return 'end'


@router.get('/t2')
def sync_test2():
    one_to_ten()
    return 'end'
