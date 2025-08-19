from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from infraestructure.db.repositories.product_repo import get_db
from infraestructure.db.repositories.user_repo import UserRepository
from domain.models.user import UserCreate, UserLogin, User
from config.security import verify_password
from domain.models.auth import Token # Tienes que crear este modelo
from datetime import timedelta
from config.jwt import create_access_token 

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    existing_user = repo.get_user_by_username(username=user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )
    
    # Crea el primer usuario como administrador si no hay usuarios en la base de datos
    is_admin = not repo.get_user_by_username(username=user.username) and repo.get_user_by_username(username="admin_user") is None
    
    db_user = repo.create_user(user, is_admin=is_admin)
    return db_user

@router.post("/login", response_model=Token)
def login_for_access_token(user_login: UserLogin, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_user_by_username(username=user_login.username)
    
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin}, # 💡 Incluye el rol de administrador
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}