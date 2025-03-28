import os
# Visual Studio Code는 다음 코드 추가 필요 #
import sys

import uvicorn
from fastapi import FastAPI, APIRouter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_1_local.controller.ai_controller_local import ai_router
from project_1_local.controller.index_controller import index_router
from project_1_local.controller.nginx_controller import nginx_router
from project_1_local.controller.sync_controller import sync_router

app = FastAPI()

api_app = APIRouter(prefix='/api')
api_app.include_router(ai_router)
api_app.include_router(nginx_router)
api_app.include_router(sync_router)

page_app = APIRouter()
page_app.include_router(index_router)

app.include_router(api_app)
app.include_router(page_app)

if __name__ == '__main__':
    uvicorn.run(app='main_local:app', host='0.0.0.0', port=8000, reload=True)
