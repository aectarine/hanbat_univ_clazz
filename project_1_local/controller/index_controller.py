from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

index_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@index_router.get('/')
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})
