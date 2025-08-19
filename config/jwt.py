# config/jwt.py
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

SECRET_KEY = "c51a029c78d5314a9b5f1a580e0d55e09f425121b6d2105e4638a1631f478c94"  # 💡 ¡Cámbiala por una cadena segura!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt