from fastapi import APIRouter
from fastapi import Depends

from dependencies import (
    get_create_user_usecase,
    get_get_user_usecase
)

from app.presentation.api.schemas.user_schema import (
    CreateUserRequest,
    UserResponse
)

router = APIRouter()

@router.post("/users")
def create_user(
    request: CreateUserRequest,
    usecase=Depends(get_create_user_usecase)
):
    user = usecase.execute(
        name=request.name,
        email=request.email
    )
    return UserResponse(
        id = user.id,
        name=user.name,
        email=user.email
        )

@router.get("/users/{user_id}")
def get_user(
    user_id: int,
    usecase=Depends(get_get_user_usecase)
):
    return usecase.execute(user_id)
    
