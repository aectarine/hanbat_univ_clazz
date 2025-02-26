from fastapi import APIRouter
from fastapi.requests import Request

router = APIRouter(prefix='/nginx')


@router.get('')
async def health():
    return {'status': 'OK'}


@router.get('/test')
async def test(request: Request):
    host = request.client.host
    port = request.client.port
    method = request.method
    url = str(request.url)
    return {
        'host': host,
        'port': port,
        'method': method,
        'url': url
    }


@router.get('/test2')
async def test2(request: Request):
    host = request.headers.get("X-Real-IP") or request.client.host
    port = request.headers.get("X-Real-Port") or request.client.port
    method = request.method
    url = str(request.url)
    data = {
        'host': host,
        'port': port,
        'method': method,
        'url': url
    }
    print(data)
    return data
