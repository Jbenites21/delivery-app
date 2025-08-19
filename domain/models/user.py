from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class User(BaseModel):
    id: UUID
    username: str
    email: str
    is_admin: bool = False
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = False

class UserLogin(BaseModel):
    username: str
    password: str