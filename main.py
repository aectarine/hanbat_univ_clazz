import uvicorn
from fastapi import FastAPI, APIRouter

from controller.ai_controller import router as ai2_router
from util.database import init_db

app = FastAPI()

api_app = APIRouter(prefix='/api')

api_app.include_router(ai2_router)

app.include_router(api_app)


@app.on_event('startup')
async def startup_event():
    await init_db()


if __name__ == '__main__':
    uvicorn.run(app='main:app', host='0.0.0.0', port=8001, reload=True)
