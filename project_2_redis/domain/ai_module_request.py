from pydantic import BaseModel, Field


class AIModuleRequest(BaseModel):
    name: str = Field(...)
    version: str = Field(min_length=5, max_length=20)
