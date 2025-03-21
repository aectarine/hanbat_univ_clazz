from pydantic import BaseModel, Field


class AIModuleRequest(BaseModel):
    name: str = Field(...)  # NN
    version: str = Field(default='2.0.0', min_length=5, max_length=20)
