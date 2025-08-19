from typing import List, Optional
from domain.models.product import Product, ProductCreate
from domain.ports.product_service import ProductService
from infraestructure.db.repositories.product_repo import ProductRepository

class ProductService(ProductService):
    """implementacion del servicio de productos que utiliza el repositorio para interactuar con la db"""

    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def create_product(self, product_data: ProductCreate) -> Product:
        """crea un nuevo producto a traves del repositorio"""
        return self.repository.create(product_data)

    def get_product(self, limit: int, offset: int) -> List[Product]:
        # 💡 La modificación va aquí
        db_products = self.repository.get_all(limit, offset)
        
        # 1. Convierte los objetos ORM de la base de datos a modelos Pydantic
        products = [Product.model_validate(p) for p in db_products]
        
        # 2. Construye la URL completa para cada imagen
        for product in products:
            if product.imagenUrl:
                # 💡 Asegúrate de que esta URL base coincida con tu configuración de Docker
                product.imagenUrl = f"http://localhost:8000{product.imagenUrl}"
        
        return products