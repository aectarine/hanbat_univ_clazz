import uvicorn
from fastapi import FastAPI, APIRouter

from controller.ai_controller_by_db_and_redis import router as ai_router
from controller.nginx_controller import router as nginx_router
from util.init_database import init_db

app = FastAPI()

api_app = APIRouter(prefix='/api')

api_app.include_router(ai_router)
api_app.include_router(nginx_router)

app.include_router(api_app)


@app.on_event('startup')
async def startup_event():
    await init_db()


if __name__ == '__main__':
    uvicorn.run(app='main:app', host='0.0.0.0', port=8002, reload=True)
