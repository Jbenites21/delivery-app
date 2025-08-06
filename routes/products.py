from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.productmodels import (
    ProductCreate, ProductUpdate, ProductResponse, 
    ProductSearchFilter, ProductCategory
)
from services.product_service import product_service

# Router para productos
router = APIRouter(prefix="/api/v1", tags=["productos"])


# ===================== PRODUCTOS =====================

@router.post("/products", response_model=dict)
async def create_product(product: ProductCreate):
    """Crear un nuevo producto"""
    result = product_service.create_product(product)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {
        "message": result["message"],
        "product": result["product"]
    }

@router.get("/products/{product_id}", response_model=dict)
async def get_product(product_id: str):
    """Obtener un producto específico por ID"""
    product = product_service.get_product(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return {
        "product": product
    }

@router.put("/products/{product_id}", response_model=dict)
async def update_product(product_id: str, product_update: ProductUpdate):
    """Actualizar un producto"""
    result = product_service.update_product(product_id, product_update)
    
    if not result["success"]:
        if result["message"] == "Producto no encontrado":
            raise HTTPException(status_code=404, detail=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    
    return {
        "message": result["message"],
        "product": result["product"]
    }

@router.delete("/products/{product_id}", response_model=dict)
async def delete_product(product_id: str):
    """Eliminar un producto"""
    result = product_service.delete_product(product_id)
    
    if not result["success"]:
        if result["message"] == "Producto no encontrado":
            raise HTTPException(status_code=404, detail=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    
    return {
        "message": result["message"]
    }

@router.get("/products", response_model=dict)
async def get_all_products(
    limit: int = Query(20, ge=1, le=100, description="Número de productos por página"),
    offset: int = Query(0, ge=0, description="Número de productos a omitir")
):
    """Obtener todos los productos con paginación"""
    products = product_service.get_all_products(limit=limit, offset=offset)
    
    return {
        "products": products,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": len(products)
        }
    }

@router.get("/products/search", response_model=dict)
async def search_products(
    search_term: Optional[str] = Query(None, description="Término de búsqueda"),
    categoria: Optional[ProductCategory] = Query(None, description="Filtrar por categoría"),
    precio_min: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    precio_max: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    limit: int = Query(20, ge=1, le=100, description="Número de productos por página"),
    offset: int = Query(0, ge=0, description="Número de productos a omitir")
):
    """Buscar productos con filtros"""
    
    # Validar que precio_min no sea mayor que precio_max
    if precio_min is not None and precio_max is not None and precio_min > precio_max:
        raise HTTPException(
            status_code=400, 
            detail="El precio mínimo no puede ser mayor que el precio máximo"
        )
    
    filters = ProductSearchFilter(
        search_term=search_term,
        categoria=categoria,
        precio_min=precio_min,
        precio_max=precio_max,
        disponible=disponible
    )
    
    products = product_service.search_products(filters, limit=limit, offset=offset)
    
    return {
        "products": products,
        "filters": {
            "search_term": search_term,
            "categoria": categoria.value if categoria else None,
            "precio_min": precio_min,
            "precio_max": precio_max,
            "disponible": disponible
        },
        "pagination": {
            "limit": limit,
            "offset": offset,
            "results": len(products)
        }
    }

@router.get("/products/category/{category}", response_model=dict)
async def get_products_by_category(
    category: ProductCategory,
    limit: int = Query(20, ge=1, le=100, description="Número de productos por página"),
    offset: int = Query(0, ge=0, description="Número de productos a omitir")
):
    """Obtener productos de una categoría específica"""
    products = product_service.get_products_by_category(category, limit=limit, offset=offset)
    
    return {
        "category": category.value,
        "products": products,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "results": len(products)
        }
    }

@router.get("/products/stats", response_model=dict)
async def get_product_stats():
    """Obtener estadísticas de productos"""
    stats = product_service.get_product_stats()
    
    return {
        "stats": stats
    }

# ===================== CATEGORÍAS =====================

@router.get("/categories", response_model=dict)
async def get_categories():
    """Obtener todas las categorías disponibles"""
    categories = [
        {"value": category.value, "name": category.value.replace("_", " ").title()}
        for category in ProductCategory
    ]
    
    return {
        "categories": categories
    }
