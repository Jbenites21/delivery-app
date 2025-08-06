from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ProductCategory(str, Enum):
    """Categorías de productos"""
    comida_rapida = "comida_rapida"
    pizzas = "pizzas"
    hamburguesas = "hamburguesas"
    pollo = "pollo"
    mariscos = "mariscos"
    bebidas = "bebidas"
    postres = "postres"
    ensaladas = "ensaladas"
    vegetariano = "vegetariano"
    mexicana = "mexicana"
    otros = "otros"


class ProductStatus(str, Enum):
    """Estados del producto"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DISCONTINUED = "discontinued"


class ProductBase(BaseModel):
    """Modelo base para productos"""
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del producto")
    precio: float = Field(..., gt=0, description="Precio del producto")
    categoria: ProductCategory = Field(..., description="Categoría del producto")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen del producto")
    disponible: bool = Field(True, description="Si el producto está disponible")
    tiempo_preparacion: Optional[int] = Field(None, ge=0, description="Tiempo de preparación en minutos")


class ProductCreate(ProductBase):
    """Modelo para crear producto"""
    pass


class ProductUpdate(BaseModel):
    """Modelo para actualizar producto"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: Optional[float] = Field(None, gt=0)
    categoria: Optional[ProductCategory] = None
    imagen_url: Optional[str] = None
    disponible: Optional[bool] = None
    tiempo_preparacion: Optional[int] = Field(None, ge=0)


class Product(ProductBase):
    """Modelo completo del producto"""
    id: str = Field(..., description="ID único del producto")
    created_at: str = Field(..., description="Fecha de creación")
    updated_at: Optional[str] = Field(None, description="Fecha de última actualización")


class ProductResponse(BaseModel):
    """Respuesta estándar para operaciones de productos"""
    status: bool
    message: str
    product: Optional[Product] = None


class ProductListResponse(BaseModel):
    """Respuesta para lista de productos"""
    status: bool
    message: str
    products: List[Product] = []
    total: int = 0


class ProductSearchFilter(BaseModel):
    """Filtros para búsqueda de productos"""
    categoria: Optional[ProductCategory] = None
    precio_min: Optional[float] = Field(None, ge=0)
    precio_max: Optional[float] = Field(None, ge=0)
    disponible: Optional[bool] = None
    search_term: Optional[str] = Field(None, description="Término de búsqueda en nombre o descripción")
