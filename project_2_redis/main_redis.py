import asyncio

import uvicorn
from fastapi import FastAPI, APIRouter

# Visual Studio Code는 다음 코드 추가 필요 #
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_2_redis.controller.ai_controller_redis import ai_router
from project_2_redis.controller.nginx_controller import nginx_router
from project_2_redis.controller.index_controller import index_router
from project_2_redis.utils.init_db import init_db
from project_2_redis.utils.init_redis import redis_listener, init_redis

app = FastAPI()

api_router = APIRouter(prefix='/api')
api_router.include_router(ai_router)
api_router.include_router(nginx_router)

page_router = APIRouter()
page_router.include_router(index_router)

app.include_router(api_router)
app.include_router(page_router)


@app.on_event('startup')
async def startup():
    await asyncio.gather(init_db(), init_redis())
    asyncio.create_task(redis_listener())


if __name__ == '__main__':
    uvicorn.run('main_redis:app', host='0.0.0.0', port=8000, reload=True)
