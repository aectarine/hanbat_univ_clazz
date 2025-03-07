from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = 'postgresql+asyncpg://postgres:0000@localhost/postgres'
ENGINE = create_async_engine(DB_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=ENGINE, class_=AsyncSession, autocommit=False, autoflush=False)
Base = declarative_base()


# 데이터베이스 초기화 함수
async def init_db():
    async with ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 비동기 컨텍스트 매니저
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
