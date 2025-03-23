from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = 'postgresql+asyncpg://postgres:0000@localhost:5432/postgres'

ENGINE = create_async_engine(DB_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=ENGINE, class_=AsyncSession, autocommit=False, autoflush=False)
Base = declarative_base()


async def init_db():
    try:
        async with ENGINE.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print('DB 연결 및 테이블 생성 완료')
    except SQLAlchemyError as e:
        print(f'DB 연결 중 오류: {e}')
        raise


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            print(f'DB 세션 오류: {e}')
            raise
        finally:
            await session.close()
