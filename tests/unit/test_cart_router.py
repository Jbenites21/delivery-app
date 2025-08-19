"""
Pruebas unitarias para el router de carrito de compras
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from fastapi import FastAPI
import uuid
import requests

# Añadir el directorio raíz al path para las importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Mock de SQLAlchemy antes de importar cualquier cosa que lo use
sys.modules['sqlalchemy'] = Mock()
sys.modules['sqlalchemy.orm'] = Mock()
sys.modules['infraestructure.db.repositories.product_repo'] = Mock()

# Crear mock para get_db
mock_get_db = Mock()
sys.modules['infraestructure.db.repositories.product_repo'].get_db = mock_get_db

# Importar el router y modelos de cart
from infraestructure.api.routers.cart import router, CartItem, CheckoutRequest
from domain.models.product import Product, ProductCategory


class TestCartModels:
    """Pruebas para los modelos de Pydantic del módulo de carrito"""
    
    def test_cart_item_model_valid_data(self):
        """Prueba creación válida del modelo CartItem"""
        item_data = {
            "product_id": "prod_123",
            "quantity": 2
        }
        cart_item = CartItem(**item_data)
        
        assert cart_item.product_id == "prod_123"
        assert cart_item.quantity == 2
    
    def test_cart_item_model_string_quantity(self):
        """Prueba que quantity acepta strings numéricos y los convierte"""
        cart_item = CartItem(product_id="prod_123", quantity="5")
        assert cart_item.quantity == 5
        assert isinstance(cart_item.quantity, int)
    
    def test_checkout_request_model_valid_data(self):
        """Prueba creación válida del modelo CheckoutRequest"""
        items = [
            {"product_id": "prod_1", "quantity": 2},
            {"product_id": "prod_2", "quantity": 1}
        ]
        checkout_data = {
            "items": items
        }
        checkout_request = CheckoutRequest(**checkout_data)
        
        assert len(checkout_request.items) == 2
        assert checkout_request.items[0].product_id == "prod_1"
        assert checkout_request.items[0].quantity == 2
    
    def test_checkout_request_model_empty_items(self):
        """Prueba CheckoutRequest con lista de items vacía"""
        checkout_data = {
            "items": []
        }
        checkout_request = CheckoutRequest(**checkout_data)
        
        assert len(checkout_request.items) == 0
    
    def test_checkout_request_model_single_item(self):
        """Prueba CheckoutRequest con un solo item"""
        checkout_data = {
            "items": [{"product_id": "prod_1", "quantity": 3}]
        }
        checkout_request = CheckoutRequest(**checkout_data)
        
        assert len(checkout_request.items) == 1
        assert checkout_request.items[0].quantity == 3


class TestCheckoutFunction:
    """Pruebas para la función checkout"""
    
    def setup_method(self):
        """Configuración inicial para cada prueba"""
        self.mock_product_1 = Product(
            id=uuid.uuid4(),
            nombre="Manzana",
            descripcion="Manzana roja fresca",
            precio=2.50,
            categoria=ProductCategory.frutasHortalizas,
            imagenUrl="/uploads/manzana.jpg",
            disponible=True
        )
        
        self.mock_product_2 = Product(
            id=uuid.uuid4(),
            nombre="Pollo",
            descripcion="Pechuga de pollo",
            precio=8.75,
            categoria=ProductCategory.carnesOtros,
            imagenUrl="/uploads/pollo.jpg",
            disponible=True
        )
    
    @patch('requests.post')
    @patch('infraestructure.api.routers.cart.ProductServiceImpl')
    def test_checkout_success_single_item(self, mock_service_class, mock_requests_post):
        """Prueba checkout exitoso con un solo item"""
        # Configurar mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_product_by_id.return_value = self.mock_product_1
        
        # Mock de la respuesta de payment API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Pago simulado exitosamente.",
            "status": "completed",
            "transaction_id": "txn_12345"
        }
        mock_requests_post.return_value = mock_response
        
        # Mock de la base de datos
        mock_db = Mock()
        
        # Crear request
        request = CheckoutRequest(items=[CartItem(product_id="prod_1", quantity=2)])
        
        # Importar la función después de los mocks
        from infraestructure.api.routers.cart import checkout
        
        # Ejecutar función
        result = checkout(request, mock_db)
        
        # Verificar resultados
        assert result["message"] == "Compra procesada exitosamente."
        assert result["total"] == 5.0  # 2.50 * 2
        assert "payment_response" in result
        assert result["payment_response"]["status"] == "completed"
        
        # Verificar que se llamaron los mocks correctamente
        mock_service.get_product_by_id.assert_called_once_with("prod_1")
        mock_requests_post.assert_called_once()
        
        # Verificar el payload enviado al payment API
        call_args = mock_requests_post.call_args
        payload = call_args[1]['json']
        assert payload['total_amount'] == 5.0
        assert len(payload['items']) == 1
        assert payload['items'][0]['product_id'] == "prod_1"
        assert payload['items'][0]['quantity'] == 2
    
    @patch('requests.post')
    @patch('infraestructure.api.routers.cart.ProductServiceImpl')
    def test_checkout_success_multiple_items(self, mock_service_class, mock_requests_post):
        """Prueba checkout exitoso con múltiples items"""
        # Configurar mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        def mock_get_product(product_id):
            if product_id == "prod_1":
                return self.mock_product_1
            elif product_id == "prod_2":
                return self.mock_product_2
            return None
        
        mock_service.get_product_by_id.side_effect = mock_get_product
        
        # Mock de la respuesta de payment API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Pago simulado exitosamente.",
            "status": "completed",
            "transaction_id": "txn_67890"
        }
        mock_requests_post.return_value = mock_response
        
        # Mock de la base de datos
        mock_db = Mock()
        
        # Crear request con múltiples items
        request = CheckoutRequest(items=[
            CartItem(product_id="prod_1", quantity=2),
            CartItem(product_id="prod_2", quantity=1)
        ])
        
        # Importar la función después de los mocks
        from infraestructure.api.routers.cart import checkout
        
        # Ejecutar función
        result = checkout(request, mock_db)
        
        # Verificar resultados
        expected_total = (2.50 * 2) + (8.75 * 1)  # 5.0 + 8.75 = 13.75
        assert result["total"] == expected_total
        assert result["message"] == "Compra procesada exitosamente."
        
        # Verificar llamadas a get_product_by_id
        assert mock_service.get_product_by_id.call_count == 2
        mock_service.get_product_by_id.assert_any_call("prod_1")
        mock_service.get_product_by_id.assert_any_call("prod_2")
    
    @patch('infraestructure.api.routers.cart.ProductServiceImpl')
    def test_checkout_product_not_found(self, mock_service_class):
        """Prueba checkout cuando un producto no existe"""
        # Configurar mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_product_by_id.return_value = None
        
        # Mock de la base de datos
        mock_db = Mock()
        
        # Crear request
        request = CheckoutRequest(items=[CartItem(product_id="prod_999", quantity=1)])
        
        # Importar la función después de los mocks
        from infraestructure.api.routers.cart import checkout
        
        # Verificar que se lance HTTPException
        with pytest.raises(HTTPException) as exc_info:
            checkout(request, mock_db)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Producto con ID prod_999 no encontrado." in str(exc_info.value.detail)
    
    @patch('requests.post')
    @patch('infraestructure.api.routers.cart.ProductServiceImpl')
    def test_checkout_payment_api_error(self, mock_service_class, mock_requests_post):
        """Prueba checkout cuando la API de pago devuelve error"""
        # Configurar mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_product_by_id.return_value = self.mock_product_1
        
        # Mock de respuesta de error de payment API
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "detail": "El monto total debe ser mayor a cero."
        }
        mock_requests_post.return_value = mock_response
        
        # Mock de la base de datos
        mock_db = Mock()
        
        # Crear request
        request = CheckoutRequest(items=[CartItem(product_id="prod_1", quantity=1)])
        
        # Importar la función después de los mocks
        from infraestructure.api.routers.cart import checkout
        
        # Verificar que se lance HTTPException
        with pytest.raises(HTTPException) as exc_info:
            checkout(request, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "El monto total debe ser mayor a cero." in str(exc_info.value.detail)
    
    @patch('requests.post')
    @patch('infraestructure.api.routers.cart.ProductServiceImpl')
    def test_checkout_payment_api_unknown_error(self, mock_service_class, mock_requests_post):
        """Prueba checkout cuando la API de pago devuelve error sin detail"""
        # Configurar mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_product_by_id.return_value = self.mock_product_1
        
        # Mock de respuesta de error sin detail
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_requests_post.return_value = mock_response
        
        # Mock de la base de datos
        mock_db = Mock()
        
        # Crear request
        request = CheckoutRequest(items=[CartItem(product_id="prod_1", quantity=1)])
        
        # Importar la función después de los mocks
        from infraestructure.api.routers.cart import checkout
        
        # Verificar que se lance HTTPException con mensaje genérico
        with pytest.raises(HTTPException) as exc_info:
            checkout(request, mock_db)
        
        assert exc_info.value.status_code == 500
        assert "Error en el procesamiento del pago." in str(exc_info.value.detail)
    
    @patch('requests.post')
    @patch('infraestructure.api.routers.cart.ProductServiceImpl')
    def test_checkout_requests_exception(self, mock_service_class, mock_requests_post):
        """Prueba checkout cuando requests.post lanza una excepción"""
        # Configurar mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_product_by_id.return_value = self.mock_product_1
        
        # Mock para que requests.post lance una excepción
        mock_requests_post.side_effect = requests.RequestException("Connection error")
        
        # Mock de la base de datos
        mock_db = Mock()
        
        # Crear request
        request = CheckoutRequest(items=[CartItem(product_id="prod_1", quantity=1)])
        
        # Importar la función después de los mocks
        from infraestructure.api.routers.cart import checkout
        
        # Verificar que se propague la excepción
        with pytest.raises(requests.RequestException):
            checkout(request, mock_db)
    
    @patch('requests.post')
    @patch('infraestructure.api.routers.cart.ProductServiceImpl')
    def test_checkout_total_calculation_accuracy(self, mock_service_class, mock_requests_post):
        """Prueba la precisión del cálculo del total con decimales"""
        # Configurar mocks con precios decimales
        mock_product_decimal = Product(
            id=uuid.uuid4(),
            nombre="Producto Decimal",
            descripcion="Producto con precio decimal",
            precio=1.99,
            categoria=ProductCategory.frutasHortalizas,
            imagenUrl="/uploads/decimal.jpg",
            disponible=True
        )
        
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_product_by_id.return_value = mock_product_decimal
        
        # Mock de la respuesta de payment API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Pago simulado exitosamente.",
            "status": "completed",
            "transaction_id": "txn_decimal"
        }
        mock_requests_post.return_value = mock_response
        
        # Mock de la base de datos
        mock_db = Mock()
        
        # Crear request con cantidad que resultará en decimal
        request = CheckoutRequest(items=[CartItem(product_id="prod_decimal", quantity=3)])
        
        # Importar la función después de los mocks
        from infraestructure.api.routers.cart import checkout
        
        # Ejecutar función
        result = checkout(request, mock_db)
        
        # Verificar cálculo preciso
        expected_total = 1.99 * 3  # 5.97
        assert result["total"] == expected_total
        assert result["total"] == 5.97


@pytest.fixture
def app():
    """Fixture que crea una app FastAPI con el router de cart"""
    from fastapi import FastAPI
    app = FastAPI()
    
    # Override dependencies to avoid database issues
    def override_get_db():
        return Mock()
    
    app.dependency_overrides = {}
    app.include_router(router)
    
    # Override the get_db dependency
    try:
        from infraestructure.db.repositories.product_repo import get_db
        app.dependency_overrides[get_db] = override_get_db
    except:
        pass
    
    return app


@pytest.fixture
def client(app):
    """Fixture que crea un cliente de pruebas"""
    return TestClient(app)


class TestCartRouter:
    """Pruebas de integración para el router de carrito"""
    
    @patch('requests.post')
    @patch('infraestructure.api.routers.cart.ProductServiceImpl')
    def test_checkout_endpoint_success(self, mock_service_class, mock_requests_post, client):
        """Prueba endpoint de checkout exitoso"""
        # Configurar mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        # Mock del producto
        mock_product = Product(
            id=uuid.uuid4(),
            nombre="Producto Test",
            descripcion="Producto para pruebas",
            precio=10.0,
            categoria=ProductCategory.frutasHortalizas,
            imagenUrl="/uploads/test.jpg",
            disponible=True
        )
        mock_service.get_product_by_id.return_value = mock_product
        
        # Mock de la respuesta de payment API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Pago simulado exitosamente.",
            "status": "completed",
            "transaction_id": "txn_endpoint_test"
        }
        mock_requests_post.return_value = mock_response
        
        # Payload para el endpoint
        payload = {
            "items": [
                {"product_id": "prod_1", "quantity": 2}
            ]
        }
        
        # Hacer request al endpoint
        response = client.post("/cart/checkout", json=payload)
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Compra procesada exitosamente."
        assert data["total"] == 20.0  # 10.0 * 2
        assert "payment_response" in data
        assert data["payment_response"]["status"] == "completed"
    
    @patch('infraestructure.api.routers.cart.ProductServiceImpl')
    def test_checkout_endpoint_product_not_found(self, mock_service_class, client):
        """Prueba endpoint cuando producto no existe"""
        # Configurar mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_product_by_id.return_value = None
        
        # Payload para el endpoint
        payload = {
            "items": [
                {"product_id": "prod_inexistente", "quantity": 1}
            ]
        }
        
        # Hacer request al endpoint
        response = client.post("/cart/checkout", json=payload)
        
        # Verificar respuesta de error
        assert response.status_code == 404
        data = response.json()
        assert "Producto con ID prod_inexistente no encontrado." in data["detail"]
    
    def test_checkout_endpoint_invalid_payload(self, client):
        """Prueba endpoint con payload inválido"""
        # Payload inválido (falta quantity)
        payload = {
            "items": [
                {"product_id": "prod_1"}  # Falta quantity
            ]
        }
        
        # Hacer request al endpoint
        response = client.post("/cart/checkout", json=payload)
        
        # Verificar error de validación
        assert response.status_code == 422
    
    @patch('requests.post')
    @patch('infraestructure.api.routers.cart.ProductServiceImpl')
    def test_checkout_endpoint_empty_items(self, mock_service_class, mock_requests_post, client):
        """Prueba endpoint con lista de items vacía"""
        # Configurar mocks para el caso de lista vacía
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        # Mock de la respuesta de payment API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Pago simulado exitosamente.",
            "status": "completed",
            "transaction_id": "txn_empty"
        }
        mock_requests_post.return_value = mock_response
        
        # Payload con lista vacía
        payload = {
            "items": []
        }
        
        # Hacer request al endpoint
        response = client.post("/cart/checkout", json=payload)
        
        # Debería procesar exitosamente con total 0
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["message"] == "Compra procesada exitosamente."
    
    def test_checkout_endpoint_missing_items(self, client):
        """Prueba endpoint sin campo items"""
        # Payload sin items
        payload = {}
        
        # Hacer request al endpoint
        response = client.post("/cart/checkout", json=payload)
        
        # Verificar error de validación
        assert response.status_code == 422
    
    def test_checkout_endpoint_invalid_json(self, client):
        """Prueba endpoint con JSON inválido"""
        # Hacer request con JSON malformado
        response = client.post("/cart/checkout", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        
        # Verificar error de parsing
        assert response.status_code == 422
