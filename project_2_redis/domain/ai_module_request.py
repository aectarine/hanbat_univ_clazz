from pydantic import BaseModel, Field


class AIModuleRequest(BaseModel):
    name: str = Field(...)
    version: str = Field(default='1.0.0', min_length=5, max_length=20)
