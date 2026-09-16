Nếu mục tiêu của bạn là học đúng tư duy enterprise backend, mình khuyên không nên bắt đầu bằng việc nhét tất cả logic vào FastAPI route.

Hãy xem FastAPI chỉ là một adapter. Business logic phải độc lập với framework. Đây chính là tinh thần của Hexagonal Architecture (Ports & Adapters).

Kiến trúc mục tiêu

Ta sẽ xây API:

POST /users
GET /users/{id}


với cấu trúc:

app/
│
├── domain/
│   ├── entities/
│   │   └── user.py
│   │
│   ├── repositories/
│   │   └── user_repository.py
│   │
│   └── services/
│       └── user_service.py
│
├── application/
│   ├── usecases/
│   │   ├── create_user.py
│   │   └── get_user.py
│
├── infrastructure/
│   ├── database/
│   │   └── models.py
│   │
│   └── repositories/
│       └── postgres_user_repository.py
│
├── presentation/
│   └── api/
│       └── user_router.py
│
├── dependencies.py
└── main.py

1. Domain Layer
Entity

domain/entities/user.py

from dataclasses import dataclass

@dataclass
class User:
    id: int | None
    name: str
    email: str

Repository Port

Đây là interface mà business phụ thuộc vào.

domain/repositories/user_repository.py

from abc import ABC, abstractmethod
from domain.entities.user import User

class UserRepository(ABC):

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        pass


Domain hoàn toàn không biết:

FastAPI
PostgreSQL
SQLAlchemy
2. Application Layer
Create User UseCase

application/usecases/create_user.py

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository

class CreateUserUseCase:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, name: str, email: str) -> User:

        user = User(
            id=None,
            name=name,
            email=email
        )

        return self.repository.save(user)

Get User UseCase

application/usecases/get_user.py

from domain.repositories.user_repository import UserRepository

class GetUserUseCase:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, user_id: int):
        return self.repository.get_by_id(user_id)

3. Infrastructure Layer
SQLAlchemy Model

infrastructure/database/models.py

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass


class UserModel(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str]

    email: Mapped[str]

PostgreSQL Repository Adapter

infrastructure/repositories/postgres_user_repository.py

from sqlalchemy.orm import Session

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository

from infrastructure.database.models import UserModel

class PostgresUserRepository(UserRepository):

    def __init__(self, session: Session):
        self.session = session

    def save(self, user: User) -> User:

        model = UserModel(
            name=user.name,
            email=user.email
        )

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        return User(
            id=model.id,
            name=model.name,
            email=model.email
        )

    def get_by_id(self, user_id: int):

        model = self.session.get(
            UserModel,
            user_id
        )

        if not model:
            return None

        return User(
            id=model.id,
            name=model.name,
            email=model.email
        )


Đây chính là Adapter của Hexagonal Architecture.

4. Dependency Injection

FastAPI có DI builtin rất mạnh.

dependencies.py

from fastapi import Depends

from application.usecases.create_user import CreateUserUseCase
from application.usecases.get_user import GetUserUseCase

from infrastructure.repositories.postgres_user_repository import (
    PostgresUserRepository
)

from infrastructure.database.session import get_session


def get_user_repository(
    session=Depends(get_session)
):
    return PostgresUserRepository(session)


def get_create_user_usecase(
    repo=Depends(get_user_repository)
):
    return CreateUserUseCase(repo)


def get_get_user_usecase(
    repo=Depends(get_user_repository)
):
    return GetUserUseCase(repo)


Dependency graph:

FastAPI Route

↓ Depends

UseCase

↓ Depends

Repository

↓ Depends

PostgreSQL Session

5. API Layer

DTO request/response.

from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

Controller

presentation/api/user_router.py

from fastapi import APIRouter
from fastapi import Depends

from dependencies import (
    get_create_user_usecase,
    get_get_user_usecase
)

router = APIRouter()


@router.post("/users")
def create_user(
    request: CreateUserRequest,
    usecase=Depends(
        get_create_user_usecase
    )
):

    user = usecase.execute(
        name=request.name,
        email=request.email
    )

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email
    )


@router.get("/users/{user_id}")
def get_user(
    user_id: int,
    usecase=Depends(
        get_get_user_usecase
    )
):
    return usecase.execute(user_id)

6. Main
from fastapi import FastAPI
from presentation.api.user_router import router

app = FastAPI()

app.include_router(router)

Tại sao đây là Hexagonal Architecture?
Business không phụ thuộc Database
UseCase
    ↓
UserRepository (Port)


UseCase chỉ biết:

repository.save()


Không biết PostgreSQL hay MongoDB.

Có thể thay adapter

Hôm nay:

PostgresUserRepository


Ngày mai:

MongoUserRepository


hoặc:

RedisUserRepository


UseCase không đổi 1 dòng.

Phiên bản "chuẩn enterprise" hơn

Khi làm production mình thường thêm:

domain/
application/
infrastructure/
presentation/

shared/
config/


và áp dụng:

FastAPI
SQLAlchemy 2.0
Alembic
PostgreSQL
Dependency Injector
Pydantic v2
pytest
Docker


Thậm chí dùng thư viện:

pip install dependency-injector


thay cho Depends để có IoC Container giống Spring Boot hoặc .NET.

Roadmap tiếp theo

Sau ví dụ này, bạn nên xây lần lượt:

CRUD User hoàn chỉnh
JWT Authentication
RBAC (Admin/User)
PostgreSQL + Alembic
Docker Compose
Redis Cache
Unit Test cho UseCase
Integration Test cho API
CQRS
Event-driven (Kafka/RabbitMQ)

Lúc đó bạn sẽ có một backend FastAPI theo chuẩn enterprise gần tương đương cách các team backend lớn triển khai microservice.