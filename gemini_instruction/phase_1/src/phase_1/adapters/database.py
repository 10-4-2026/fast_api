'''
Bước 3: Cấu hình SQLAlchemy 2.0 (Async Engine & Session)
Tại src/adapters/database.py, thiết lập kết nối cơ sở dữ liệu bất đồng bộ sử dụng async_sessionmaker.
'''

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Sử dụng SQLite async hoặc PostgreSQL (ví dụ dùng SQLite cho môi trường test nhanh)
DATABASE_URL = "sqlite+aiosqlite:///./iot_platform.db"

engine = create_async_engine(
    DATABASE_URL,
    echo = True,
    future=True
)

async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# Dependency tiêm Session cho FastAPI Router
async def get_db_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
            pass
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            pass            
        pass
