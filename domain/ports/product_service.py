from abc import ABC, abstractmethod
from typing import List
from ..models.product import Product, ProductCreate

class ProductService(ABC):
    """puerto abstracto para el ProductService"""

    @abstractmethod
    def create_product(self, product_data: ProductCreate) -> Product:
        """Crea un nuevo producto y lo devuelve"""
        pass

    @abstractmethod
    def get_product(self, limit: int, offset:int) -> List[Product]:
        """Obtiene una lista de productos paginada"""
        pass