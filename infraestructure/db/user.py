import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import declarative_base # Asegúrate de que importas Base desde el archivo correcto

Base = declarative_base()

class UserORM(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)