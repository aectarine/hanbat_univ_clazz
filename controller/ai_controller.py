from fastapi import APIRouter

router = APIRouter(prefix='/ai')

task = list()


@router.get('')
def get_ai():
    pass


@router.post('')
def create_ai():
    pass


@router.put('')
def modify_ai():
    pass


@router.delete('')
def remove_ai():
    pass
