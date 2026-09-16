from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository

class CreateUserUseCase:

    def __init__(self, repository: UserRepository):
        self.repository = repository
        pass

    def execute(self, name: str, email: str) -> User:

        user = User (
            id=None,
            name=name,
            email=email
        )

        return self.repository.save(user)

    pass