from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/')
async def index(req: Request):
    return templates.TemplateResponse('index.html', {'request': req})
