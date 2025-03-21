import asyncio

import uvicorn
from fastapi import FastAPI, APIRouter

from project_2_redis.controller.ai_controller_redis import ai_router
from project_2_redis.controller.index_controller import index_router
from project_2_redis.utils.init_db import init_db
from project_2_redis.utils.init_redis import redis_listener, init_redis

app = FastAPI()

api_router = APIRouter(prefix='/api')
api_router.include_router(ai_router)

page_router = APIRouter()
page_router.include_router(index_router)

app.include_router(api_router)
app.include_router(page_router)


@app.on_event('startup')
async def startup():
    await asyncio.gather(init_db(), init_redis())
    asyncio.create_task(redis_listener())


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
