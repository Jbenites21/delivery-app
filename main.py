from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from infraestructure.api.routers import product, auth, payment

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Delivery App", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a los orígenes permitidos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(product.router)
app.include_router(auth.router)
app.include_router(payment.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Delivery App API"}
