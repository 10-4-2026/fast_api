from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///app.cb"

engine = create_engine(DATABASE_URL)