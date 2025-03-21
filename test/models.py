from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum


class AI_Module(Base):
    __tablename__ = 'ai_module'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False, default='1.0.0')
    status = Column(Enum(StatusType), nullable=False, default=StatusType.STOP)
    inserted = Column(DateTime, default=datetime.now())
    updated = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
