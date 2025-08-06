"""
Pruebas unitarias para los endpoints de productos
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from main import app
from models.productmodels import ProductCategory


class TestProductRoutes:
    """Pruebas para los endpoints de productos"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_product_service(self):
        """Mock del servicio de productos"""
        with patch('routes.products.product_service') as mock:
            yield mock
    
    def test_create_product_success(self, client, mock_product_service, sample_product_data):
        """Crear producto exitosamente"""
        # Configurar mock
        mock_product_service.create_product.return_value = {
            "success": True,
            "message": "Producto creado exitosamente",
            "product": {"id": "test-id", **sample_product_data}
        }
        
        # Ejecutar
        response = client.post("/api/v1/products", json=sample_product_data)
        
        # Verificar
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Producto creado exitosamente"
        assert "product" in data
        mock_product_service.create_product.assert_called_once()
    
    def test_create_product_validation_error(self, client):
        """Crear producto con datos inválidos"""
        invalid_data = {
            "nombre": "",  # Nombre vacío
            "precio": -10,  # Precio negativo
            "categoria": "categoria_invalida"
        }
        
        response = client.post("/api/v1/products", json=invalid_data)
        
        assert response.status_code == 422
        assert "detail" in response.json()
    
    def test_create_product_service_error(self, client, mock_product_service, sample_product_data):
        """Error del servicio al crear producto"""
        # Configurar mock para error
        mock_product_service.create_product.return_value = {
            "success": False,
            "message": "Error interno del servicio"
        }
        
        response = client.post("/api/v1/products", json=sample_product_data)
        
        assert response.status_code == 400
        assert "Error interno del servicio" in response.json()["detail"]
    
    def test_get_product_success(self, client, mock_product_service):
        """Obtener producto existente"""
        # Configurar mock
        mock_product_service.get_product.return_value = {
            "success": True,
            "product": {
                "id": "test-id",
                "nombre": "Pizza Margherita",
                "precio": 15.99
            }
        }
        
        response = client.get("/api/v1/products/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["product"]["nombre"] == "Pizza Margherita"
        mock_product_service.get_product.assert_called_once_with("test-id")
    
    def test_get_product_not_found(self, client, mock_product_service):
        """Obtener producto no existente"""
        # Configurar mock
        mock_product_service.get_product.return_value = {
            "success": False,
            "message": "Producto no encontrado"
        }
        
        response = client.get("/api/v1/products/non-existent")
        
        assert response.status_code == 404
        assert "Producto no encontrado" in response.json()["detail"]
    
    def test_get_all_products(self, client, mock_product_service):
        """Obtener todos los productos"""
        # Configurar mock
        mock_products = [
            {"id": "1", "nombre": "Producto 1"},
            {"id": "2", "nombre": "Producto 2"}
        ]
        mock_product_service.get_all_products.return_value = mock_products
        
        response = client.get("/api/v1/products")
        
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "pagination" in data
        assert len(data["products"]) == 2
        mock_product_service.get_all_products.assert_called_once_with(limit=20, offset=0)
    
    def test_get_all_products_with_pagination(self, client, mock_product_service):
        """Obtener productos con paginación"""
        mock_product_service.get_all_products.return_value = []
        
        response = client.get("/api/v1/products?limit=10&offset=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["limit"] == 10
        assert data["pagination"]["offset"] == 5
        mock_product_service.get_all_products.assert_called_once_with(limit=10, offset=5)
    
    def test_update_product_success(self, client, mock_product_service):
        """Actualizar producto exitosamente"""
        update_data = {"nombre": "Nuevo nombre", "precio": 20.99}
        mock_product_service.update_product.return_value = {
            "success": True,
            "message": "Producto actualizado exitosamente",
            "product": {"id": "test-id", **update_data}
        }
        
        response = client.put("/api/v1/products/test-id", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Producto actualizado exitosamente"
        mock_product_service.update_product.assert_called_once()
    
    def test_update_product_not_found(self, client, mock_product_service):
        """Actualizar producto no existente"""
        update_data = {"nombre": "Nuevo nombre"}
        mock_product_service.update_product.return_value = {
            "success": False,
            "message": "Producto no encontrado"
        }
        
        response = client.put("/api/v1/products/non-existent", json=update_data)
        
        assert response.status_code == 404
        assert "Producto no encontrado" in response.json()["detail"]
    
    def test_delete_product_success(self, client, mock_product_service):
        """Eliminar producto exitosamente"""
        mock_product_service.delete_product.return_value = {
            "success": True,
            "message": "Producto eliminado exitosamente"
        }
        
        response = client.delete("/api/v1/products/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Producto eliminado exitosamente"
        mock_product_service.delete_product.assert_called_once_with("test-id")
    
    def test_delete_product_not_found(self, client, mock_product_service):
        """Eliminar producto no existente"""
        mock_product_service.delete_product.return_value = {
            "success": False,
            "message": "Producto no encontrado"
        }
        
        response = client.delete("/api/v1/products/non-existent")
        
        assert response.status_code == 404
        assert "Producto no encontrado" in response.json()["detail"]
    
    def test_search_products(self, client, mock_product_service):
        """Buscar productos con filtros"""
        mock_products = [{"id": "1", "nombre": "Pizza Margherita"}]
        mock_product_service.search_products.return_value = mock_products
        
        response = client.get("/api/v1/products/search?search_term=pizza&categoria=pizzas")
        
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "filters" in data
        assert data["filters"]["search_term"] == "pizza"
        assert data["filters"]["categoria"] == "pizzas"
        mock_product_service.search_products.assert_called_once()
    
    def test_search_products_price_validation(self, client):
        """Validar que precio_min no sea mayor que precio_max"""
        response = client.get("/api/v1/products/search?precio_min=20&precio_max=10")
        
        assert response.status_code == 400
        assert "precio mínimo no puede ser mayor" in response.json()["detail"]
    
    def test_get_products_by_category(self, client, mock_product_service):
        """Obtener productos por categoría"""
        mock_products = [{"id": "1", "nombre": "Pizza 1", "categoria": "pizzas"}]
        mock_product_service.get_products_by_category.return_value = mock_products
        
        response = client.get("/api/v1/products/category/pizzas")
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "pizzas"
        assert "products" in data
        mock_product_service.get_products_by_category.assert_called_once()
    
    def test_get_product_stats(self, client, mock_product_service):
        """Obtener estadísticas de productos"""
        mock_stats = {
            "total_products": 10,
            "available_count": 8,
            "unavailable_count": 2,
            "by_category": {"pizzas": 5, "hamburguesas": 3}
        }
        mock_product_service.get_product_stats.return_value = mock_stats
        
        response = client.get("/api/v1/products/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["stats"]["total_products"] == 10
        assert data["stats"]["available_count"] == 8
        mock_product_service.get_product_stats.assert_called_once()
    
    def test_get_categories(self, client):
        """Obtener todas las categorías"""
        response = client.get("/api/v1/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        
        # Verificar que todas las categorías están presentes
        category_values = [cat["value"] for cat in data["categories"]]
        assert "pizzas" in category_values
        assert "hamburguesas" in category_values
        assert "bebidas" in category_values


class TestAuthenticationRoutes:
    """Pruebas para los endpoints de autenticación"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_redis(self):
        """Mock de Redis para autenticación"""
        with patch('main.redis_conn') as mock:
            mock.is_connected.return_value = True
            mock.get.return_value = None
            mock.set.return_value = True
            mock.hgetall.return_value = {}
            mock.hset.return_value = True
            yield mock
    
    def test_register_success(self, client, mock_redis, sample_user_data):
        """Registrar usuario exitosamente"""
        # Configurar mock para usuario no existente
        mock_redis.hgetall.return_value = {}
        
        response = client.post("/register", json=sample_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Usuario registrado exitosamente"
        assert "token" in data
        mock_redis.hset.assert_called()
    
    def test_register_user_exists(self, client, mock_redis, sample_user_data):
        """Registrar usuario que ya existe"""
        # Configurar mock para usuario existente
        mock_redis.hgetall.return_value = {"username": "testuser"}
        
        response = client.post("/register", json=sample_user_data)
        
        assert response.status_code == 400
        assert "Usuario ya existe" in response.json()["detail"]
    
    def test_register_validation_error(self, client):
        """Registrar con datos inválidos"""
        invalid_data = {
            "username": "",  # Username vacío
            "email": "invalid-email",  # Email inválido
            "password": "123"  # Password muy corto
        }
        
        response = client.post("/register", json=invalid_data)
        
        assert response.status_code == 422
    
    def test_login_success(self, client, mock_redis, sample_login_data):
        """Login exitoso"""
        # Configurar mock para usuario existente con password correcto
        mock_redis.hgetall.return_value = {
            "username": "testuser",
            "password_hash": "hashed_password"
        }
        
        with patch('main.verify_password', return_value=True):
            response = client.post("/login", json=sample_login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login exitoso"
        assert "token" in data
    
    def test_login_user_not_found(self, client, mock_redis, sample_login_data):
        """Login con usuario no existente"""
        # Configurar mock para usuario no existente
        mock_redis.hgetall.return_value = {}
        
        response = client.post("/login", json=sample_login_data)
        
        assert response.status_code == 401
        assert "Credenciales inválidas" in response.json()["detail"]
    
    def test_login_wrong_password(self, client, mock_redis, sample_login_data):
        """Login con contraseña incorrecta"""
        # Configurar mock para usuario existente con password incorrecto
        mock_redis.hgetall.return_value = {
            "username": "testuser",
            "password_hash": "hashed_password"
        }
        
        with patch('main.verify_password', return_value=False):
            response = client.post("/login", json=sample_login_data)
        
        assert response.status_code == 401
        assert "Credenciales inválidas" in response.json()["detail"]
    
    def test_verify_session_valid(self, client, mock_redis):
        """Verificar sesión válida"""
        # Configurar mock para sesión válida
        mock_redis.get.return_value = "testuser"
        
        response = client.get("/verify-session", headers={"Authorization": "Bearer valid-token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["username"] == "testuser"
    
    def test_verify_session_invalid(self, client, mock_redis):
        """Verificar sesión inválida"""
        # Configurar mock para sesión inválida
        mock_redis.get.return_value = None
        
        response = client.get("/verify-session", headers={"Authorization": "Bearer invalid-token"})
        
        assert response.status_code == 401
        assert "Sesión inválida" in response.json()["detail"]
    
    def test_verify_session_no_token(self, client):
        """Verificar sesión sin token"""
        response = client.get("/verify-session")
        
        assert response.status_code == 401
        assert "Token requerido" in response.json()["detail"]
    
    def test_logout_success(self, client, mock_redis):
        """Logout exitoso"""
        response = client.post("/logout", headers={"Authorization": "Bearer valid-token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Sesión cerrada exitosamente"
        mock_redis.delete.assert_called()
    
    def test_root_endpoint(self, client):
        """Probar endpoint raíz"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "Delivery App API" in data["message"]
        assert "version" in data
