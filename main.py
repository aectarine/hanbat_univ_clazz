import uvicorn
from fastapi import FastAPI, APIRouter

from controller.ai_controller import router as ai_router
from controller.async_controller import router as async_router
from controller.sync_controller import router as sync_router

app = FastAPI()

api_app = APIRouter(prefix='/api')

api_app.include_router(sync_router)
api_app.include_router(async_router)
api_app.include_router(ai_router)

app.include_router(api_app)

if __name__ == '__main__':
    uvicorn.run(app='main:app', host='0.0.0.0', port=8001, reload=True)
