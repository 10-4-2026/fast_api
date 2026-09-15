from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/mydb"
)


engine = create_async_engine(
    DATABASE_URL, echo=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
    