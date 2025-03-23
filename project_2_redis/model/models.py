from sqlalchemy import Column, Integer, String, DateTime, Enum, func

from project_2_redis.model.enums import StatusType
from project_2_redis.utils.init_db import Base


class AI_Module(Base):
    __tablename__ = 'ai_module'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False, default='1.0.0')
    status = Column(Enum(StatusType), nullable=False, default=StatusType.STOP)
    inserted = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())
