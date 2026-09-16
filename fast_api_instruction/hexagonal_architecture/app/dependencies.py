from fastapi import Depends

from app.application.usecases.create_user import CreateUserUseCase
from app.application.usecases.get_user import GetUserUseCase

from app.infrastructure.repositories.postgres_user_repository import (
    PostgreUserRepository
)

from app.infrastructure.database.session import get_session

def get_user_repository(
        session = Depends(get_session)    
):
    '''
    Gọi get_session()
        ↓
    Lấy Session
        ↓
    Truyền Session vào biến session
    
    tuong duong
    
    session = get_session()
    
    repo = PostgreUserRepository(
        session=session
    )
    '''
    '''
    Tạo Repository Dependency
    Kết quả

FastAPI tạo ra:

PostgreUserRepository(
session=session
)
Show more lines

và trả về object repository.

--------

so do hien tai

get_session()
      ↓
SQLAlchemy Session
      ↓
PostgreUserRepository(session)
    '''
    return PostgreUserRepository(session=session)

def get_create_user_usecase(
        repo=Depends(get_user_repository)                
):
    return CreateUserUseCase(repository=repo)


def get_get_user_usecase(repo=Depends(get_user_repository)):
    '''
    Depends(get_user_repository) ==
    Hãy gọi hàm get_user_repository() và inject kết quả vào đây
    

    '''
    return GetUserUseCase(repository=repo)
