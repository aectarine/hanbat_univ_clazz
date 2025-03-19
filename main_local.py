import uvicorn
from fastapi import FastAPI, APIRouter

from controller.ai_controller_local import router
from controller.index_controller import router as index_router

app = FastAPI()

# API 라우터 적용
api_app = APIRouter(prefix='/api')
api_app.include_router(router)

# HTML 라우터 적용
page_app = APIRouter()
page_app.include_router(index_router)

# FastAPI에 라우터 최종 적용
app.include_router(api_app)
app.include_router(page_app)

if __name__ == '__main__':
    uvicorn.run(app='main_local:app', host='0.0.0.0', port=8000, reload=True)
