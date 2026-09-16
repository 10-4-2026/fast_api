from app.domain.repositories.user_repository import UserRepository

class GetUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        pass

    def execute(self, user_id: str):
        return self.repository.get_by_id(user_id=user_id)
    
    pass