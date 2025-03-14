import asyncio

import uvicorn
from controller.ai_controller_by_db_and_redis import router as ai_router
from fastapi import FastAPI, APIRouter

from controller.index_controller import router as index_router
from controller.nginx_controller import router as nginx_router
from util.init_database import init_db
from util.init_redis import init_redis, redis_listener

app = FastAPI()

# API 라우터 적용
api_app = APIRouter(prefix='/api')

api_app.include_router(ai_router)
api_app.include_router(nginx_router)

app.include_router(api_app)

# HTML 라우터 적용
page_app = APIRouter()

page_app.include_router(index_router)

app.include_router(page_app)


@app.on_event('startup')
async def startup_event():
    await asyncio.gather(init_db(), init_redis())
    asyncio.create_task(redis_listener())


if __name__ == '__main__':
    uvicorn.run(app='main:app', host='0.0.0.0', port=8001, reload=True)
    # uvicorn.run(app='main:app', host='0.0.0.0', port=8000, reload=True, workers=1)
