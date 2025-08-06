from pydantic import BaseModel
from typing import Optional

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    nombre: str
    email: str
    password: str

class LoginResponse(BaseModel):
    status: bool
    message: str
    token: Optional[str] = None
    username: Optional[str] = None

class RegisterResponse(BaseModel):
    status: bool
    message: str
    token: Optional[str] = None
    username: Optional[str] = None

class UserSession(BaseModel):
    email: str
    nombre: str
    created_at: str