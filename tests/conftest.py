"""
Configuración global de fixtures para pytest
"""

import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
from models.productmodels import ProductCategory, ProductCreate, Product


@pytest.fixture
def mock_redis():
    """Mock del cliente Redis"""
    mock = Mock()
    
    # Configurar métodos del RedisConnection
    mock.is_connected.return_value = True
    mock.set_data.return_value = True
    mock.get_data.return_value = None
    mock.delete_data.return_value = True
    mock.exists.return_value = False
    mock.get_all_keys.return_value = []
    
    return mock


@pytest.fixture
def sample_product_data():
    """Datos de ejemplo para crear productos"""
    return {
        "nombre": "Pizza Margherita",
        "descripcion": "Pizza clásica con tomate, mozzarella y albahaca",
        "precio": 15.99,
        "categoria": ProductCategory.pizzas,
        "imagen_url": "https://example.com/pizza.jpg",
        "disponible": True,
        "tiempo_preparacion": 25
    }


@pytest.fixture
def sample_product_create(sample_product_data):
    """Instancia de ProductCreate para pruebas"""
    return ProductCreate(**sample_product_data)


@pytest.fixture
def sample_product():
    """Producto de ejemplo completo"""
    return Product(
        id="75cbbd01-bb9f-4c31-a8dc-b4ec6618bbeb",
        nombre="Pizza Margherita",
        descripcion="Pizza clásica con tomate, mozzarella y albahaca",
        precio=15.99,
        categoria=ProductCategory.pizzas,
        imagen_url="https://example.com/pizza.jpg",
        disponible=True,
        tiempo_preparacion=None,
        created_at="1754506472",
        updated_at=None
    )


@pytest.fixture
def test_client():
    """Cliente de pruebas para FastAPI"""
    from main import app
    return TestClient(app)


@pytest.fixture
def mock_product_service():
    """Mock del servicio de productos"""
    service = Mock()
    
    # Configurar métodos típicos del servicio
    service.create_product.return_value = {
        "success": True,
        "message": "Producto creado exitosamente",
        "product": {
            "id": "test-product-id",
            "nombre": "Pizza Margherita",
            "precio": 15.99,
            "categoria": "pizzas",
            "disponible": True
        }
    }
    
    service.get_product.return_value = {
        "id": "test-product-id",
        "nombre": "Pizza Margherita",
        "precio": 15.99,
        "categoria": "pizzas",
        "disponible": True
    }
    
    service.get_all_products.return_value = {
        "success": True,
        "products": [],
        "total": 0
    }
    
    service.update_product.return_value = {
        "success": True,
        "message": "Producto actualizado exitosamente",
        "product": {}
    }
    
    service.delete_product.return_value = {
        "success": True,
        "message": "Producto eliminado exitosamente"
    }
    
    return service


@pytest.fixture
def mock_user_data():
    """Datos de usuario para pruebas de autenticación"""
    return {
        "nombre": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
