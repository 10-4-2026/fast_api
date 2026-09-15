from abc import ABC, abstractmethod
from app.domain.entities.user import User

class UserRepository(ABC):

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        pass
    pass
