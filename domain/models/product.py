from pydantic import BaseModel, Field, config, ConfigDict
from typing import Optional
from enum import Enum
import uuid

class ProductCategory(str, Enum):
    """categoria de productos"""
    frutasHortalizas = "frutas_hortalizas"
    congelados = "congelados"
    carnesOtros = "carnes_otros"

class Product(BaseModel):
    """modelo de dominio principal para productos"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    nombre: str = Field(..., Length = 100)
    descripcion: Optional[str] = Field(None, length=500)
    precio: float = Field(..., gt=0)
    categoria: ProductCategory
    imagenUrl: Optional[str] = None
    disponible: bool = True

    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: float = Field(..., gt=0)
    categoria: ProductCategory
    imagenUrl: Optional[str] = None
    disponible: bool = True