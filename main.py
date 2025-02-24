import uvicorn
from fastapi import FastAPI

from controller.ai_controller import router as ai_router
from controller.async_controller import router as async_router
from controller.sync_controller import router as sync_router

app = FastAPI()
app.include_router(sync_router)
app.include_router(async_router)
app.include_router(ai_router)

if __name__ == '__main__':
    uvicorn.run(app='main:app', host='0.0.0.0', port=8001, reload=True)
