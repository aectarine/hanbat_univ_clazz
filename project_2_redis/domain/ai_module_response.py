from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIModuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    version: str
    status: str
    inserted: datetime
    updated: datetime
