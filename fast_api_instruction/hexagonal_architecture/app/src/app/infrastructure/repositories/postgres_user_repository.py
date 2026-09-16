from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository

from app.infrastructure.database.models import UserModel

class PostgreUserRepository(UserRepository):

    def __init__(self, session: Session):
        self.session = session

    def save(self, user: User) -> User:

        model = UserModel(
            name=user.name,
            email = user.email
        )

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        return User(
            id=model.id,
            name=model.name,
            email=model.email
        )
        pass

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
         
    pass
 
