import os
import shutil
import uuid
from typing import List, Optional
from slugify import slugify
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from domain.models.product import Product, ProductCreate, ProductCategory
from infraestructure.db.repositories.product_repo import ProductRepository, get_db
from infraestructure.services.product import ProductService as ProductServiceImpl
from domain.ports.product_service import ProductService as ProductServiceInterface
from pathlib import Path

UPLOADS_DIR = Path("/app/uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/products", tags=["products"])

def get_product_service(db: Session = Depends(get_db)):
    repository = ProductRepository(db)
    service = ProductServiceImpl(repository)
    return service

@router.post("/", response_model=dict)
async def create_product(
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    precio: float = Form(...),
    categoria: ProductCategory = Form(...),
    disponible: bool = Form(True),
    imagenUrl: UploadFile = File(...),
    product_service: ProductServiceImpl = Depends(get_product_service)
):
    """crea el nuevo producto"""
    unique_filename = f"{uuid.uuid4()}_{imagenUrl.filename}"
    file_path = UPLOADS_DIR / unique_filename

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await imagenUrl.read()
            await out_file.write(content)

        imagenUrl = f"/uploads/{unique_filename}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")
    
    product_data=ProductCreate(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        categoria=categoria,
        imagenUrl=imagenUrl,
        disponible=disponible
    )
    product = product_service.create_product(product_data)

    if product.imagenUrl:
        complete_url = f"http://localhost:8000{product.imagenUrl}"
    product.imagenUrl = complete_url
    return {"message": "Product created successfully", "product": product.model_dump()}

@router.get("/", response_model=List[Product])
def get_all_products(
    limit: int = 20,
    offset: int = 0,
    product_service: ProductServiceInterface = Depends(get_product_service)
):
    """obtiene lista de todos los productos con paginacion"""
    return product_service.get_product(limit, offset)
