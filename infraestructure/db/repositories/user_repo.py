from sqlalchemy.orm import Session
from infraestructure.db.user import UserORM
from domain.models.user import UserCreate
from config.security import get_password_hash

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate, is_admin: bool = False):
        hashed_password = get_password_hash(user.password)
        db_user = UserORM(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            is_admin=is_admin
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_username(self, username: str):
        return self.db.query(UserORM).filter(UserORM.username == username).first()