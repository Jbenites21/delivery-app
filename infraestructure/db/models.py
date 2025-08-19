import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, Enum, Text
from sqlalchemy.orm import declarative_base
from domain.models.product import Product, ProductCategory

Base = declarative_base()

class ProductORM(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), index=True,nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float)
    categoria = Column(Enum(ProductCategory))
    imagenUrl = Column(String, nullable=True)
    disponible = Column(Boolean, default=True)