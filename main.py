from fastapi import FastAPI
from pydantic import BaseModel
from models import usermodels
app = FastAPI()



@app.post("/login")
async def login(user: usermodels.UserLogin):
    print(f"User {user.email} is trying to log in with password {user.password}")
    return {
        "status": True,
        "message": "Login successful",
        "token": "1234567890abcdef",
        "username": user.username
    }

@app.post("/registrar")
async def registrar(user: usermodels.UserRegister):
    print(f"User {user.nombre} is trying to register with password {user.password} and email {user.email}")
    return {
        "status": True,
        "message": "Registration successful",
        "token": "1234567890abcdef",
        "username": user.nombre
    }