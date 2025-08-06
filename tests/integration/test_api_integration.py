"""
Pruebas de integración para la API completa
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json
import time

from main import app


class TestIntegrationProducts:
    """Pruebas de integración para el flujo completo de productos"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_redis_integration(self):
        """Mock de Redis para pruebas de integración"""
        # Simular un almacén en memoria para las pruebas
        storage = {}
        
        def mock_exists(key):
            return key in storage
        
        def mock_hgetall(key):
            return storage.get(key, {})
        
        def mock_hset(key, field=None, value=None, mapping=None):
            if key not in storage:
                storage[key] = {}
            if mapping:
                storage[key].update(mapping)
            elif field and value:
                storage[key][field] = value
            return True
        
        def mock_delete(key):
            if key in storage:
                del storage[key]
                return True
            return False
        
        def mock_scan_iter(match=None):
            keys = []
            if match:
                pattern = match.replace('*', '')
                keys = [k for k in storage.keys() if pattern in k]
            else:
                keys = list(storage.keys())
            return iter(keys)
        
        with patch('database.redis_connection.redis_conn') as mock_conn:
            mock_conn.is_connected.return_value = True
            mock_conn.exists.side_effect = mock_exists
            mock_conn.hgetall.side_effect = mock_hgetall
            mock_conn.hset.side_effect = mock_hset
            mock_conn.delete.side_effect = mock_delete
            mock_conn.scan_iter.side_effect = mock_scan_iter
            yield mock_conn, storage
    
    @pytest.mark.integration
    def test_complete_product_lifecycle(self, client, mock_redis_integration):
        """Probar el ciclo completo de vida de un producto"""
        mock_conn, storage = mock_redis_integration
        
        # 1. Crear un producto
        product_data = {
            "nombre": "Pizza Integral",
            "descripcion": "Pizza con masa integral y vegetales",
            "precio": 18.99,
            "categoria": "pizzas",
            "disponible": True,
            "imagen_url": "https://example.com/pizza-integral.jpg"
        }
        
        create_response = client.post("/api/v1/products", json=product_data)
        assert create_response.status_code == 200
        create_data = create_response.json()
        product_id = create_data["product"]["id"]
        
        # 2. Verificar que el producto se puede obtener
        get_response = client.get(f"/api/v1/products/{product_id}")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["product"]["nombre"] == "Pizza Integral"
        assert get_data["product"]["precio"] == 18.99
        
        # 3. Actualizar el producto
        update_data = {
            "nombre": "Pizza Integral Premium",
            "precio": 22.99
        }
        update_response = client.put(f"/api/v1/products/{product_id}", json=update_data)
        assert update_response.status_code == 200
        
        # 4. Verificar la actualización
        get_updated_response = client.get(f"/api/v1/products/{product_id}")
        assert get_updated_response.status_code == 200
        updated_data = get_updated_response.json()
        assert updated_data["product"]["nombre"] == "Pizza Integral Premium"
        assert updated_data["product"]["precio"] == 22.99
        
        # 5. Verificar que aparece en la lista general
        list_response = client.get("/api/v1/products")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert len(list_data["products"]) == 1
        assert list_data["products"][0]["id"] == product_id
        
        # 6. Eliminar el producto
        delete_response = client.delete(f"/api/v1/products/{product_id}")
        assert delete_response.status_code == 200
        
        # 7. Verificar que ya no existe
        get_deleted_response = client.get(f"/api/v1/products/{product_id}")
        assert get_deleted_response.status_code == 404
    
    @pytest.mark.integration
    def test_search_and_filter_products(self, client, mock_redis_integration):
        """Probar búsqueda y filtrado de productos"""
        mock_conn, storage = mock_redis_integration
        
        # Crear varios productos de prueba
        products = [
            {
                "nombre": "Pizza Margherita",
                "descripcion": "Pizza clásica italiana",
                "precio": 15.99,
                "categoria": "pizzas",
                "disponible": True
            },
            {
                "nombre": "Hamburguesa Clásica",
                "descripcion": "Hamburguesa con carne y vegetales",
                "precio": 12.50,
                "categoria": "hamburguesas",
                "disponible": True
            },
            {
                "nombre": "Pizza Vegetariana",
                "descripcion": "Pizza con vegetales frescos",
                "precio": 17.99,
                "categoria": "pizzas",
                "disponible": False
            }
        ]
        
        product_ids = []
        for product in products:
            response = client.post("/api/v1/products", json=product)
            assert response.status_code == 200
            product_ids.append(response.json()["product"]["id"])
        
        # Probar búsqueda por término
        search_response = client.get("/api/v1/products/search?search_term=pizza")
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert len(search_data["products"]) == 2
        
        # Probar filtro por categoría
        category_response = client.get("/api/v1/products/category/pizzas")
        assert category_response.status_code == 200
        category_data = category_response.json()
        assert len(category_data["products"]) == 2
        assert category_data["category"] == "pizzas"
        
        # Probar filtro por disponibilidad
        available_response = client.get("/api/v1/products/search?disponible=true")
        assert available_response.status_code == 200
        available_data = available_response.json()
        assert len(available_data["products"]) == 2
        
        # Probar filtro por rango de precios
        price_response = client.get("/api/v1/products/search?precio_min=15&precio_max=20")
        assert price_response.status_code == 200
        price_data = price_response.json()
        assert len(price_data["products"]) == 2  # Las dos pizzas
    
    @pytest.mark.integration
    def test_product_categories_endpoint(self, client):
        """Probar endpoint de categorías"""
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        
        # Verificar estructura de categorías
        for category in data["categories"]:
            assert "value" in category
            assert "name" in category
            assert isinstance(category["value"], str)
            assert isinstance(category["name"], str)
    
    @pytest.mark.integration
    def test_product_stats_endpoint(self, client, mock_redis_integration):
        """Probar endpoint de estadísticas"""
        mock_conn, storage = mock_redis_integration
        
        # Crear productos para estadísticas
        products = [
            {"nombre": "Pizza 1", "precio": 15.99, "categoria": "pizzas", "disponible": True},
            {"nombre": "Pizza 2", "precio": 17.99, "categoria": "pizzas", "disponible": False},
            {"nombre": "Hamburguesa 1", "precio": 12.50, "categoria": "hamburguesas", "disponible": True}
        ]
        
        for product in products:
            response = client.post("/api/v1/products", json=product)
            assert response.status_code == 200
        
        # Obtener estadísticas
        stats_response = client.get("/api/v1/products/stats")
        assert stats_response.status_code == 200
        
        stats_data = stats_response.json()
        assert "stats" in stats_data
        stats = stats_data["stats"]
        
        assert stats["total_products"] == 3
        assert stats["available_count"] == 2
        assert stats["unavailable_count"] == 1
        assert stats["by_category"]["pizzas"] == 2
        assert stats["by_category"]["hamburguesas"] == 1
    
    @pytest.mark.integration
    def test_pagination(self, client, mock_redis_integration):
        """Probar paginación en diferentes endpoints"""
        mock_conn, storage = mock_redis_integration
        
        # Crear 5 productos
        for i in range(1, 6):
            product = {
                "nombre": f"Producto {i}",
                "precio": 10.0 + i,
                "categoria": "pizzas",
                "disponible": True
            }
            response = client.post("/api/v1/products", json=product)
            assert response.status_code == 200
        
        # Probar primera página
        page1_response = client.get("/api/v1/products?limit=2&offset=0")
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        assert len(page1_data["products"]) == 2
        assert page1_data["pagination"]["limit"] == 2
        assert page1_data["pagination"]["offset"] == 0
        
        # Probar segunda página
        page2_response = client.get("/api/v1/products?limit=2&offset=2")
        assert page2_response.status_code == 200
        page2_data = page2_response.json()
        assert len(page2_data["products"]) == 2
        assert page2_data["pagination"]["offset"] == 2
        
        # Probar última página
        page3_response = client.get("/api/v1/products?limit=2&offset=4")
        assert page3_response.status_code == 200
        page3_data = page3_response.json()
        assert len(page3_data["products"]) == 1  # Solo queda 1 producto
    
    @pytest.mark.integration
    def test_error_handling(self, client, mock_redis_integration):
        """Probar manejo de errores en flujos completos"""
        mock_conn, storage = mock_redis_integration
        
        # Intentar obtener producto inexistente
        response = client.get("/api/v1/products/nonexistent-id")
        assert response.status_code == 404
        
        # Intentar actualizar producto inexistente
        update_response = client.put("/api/v1/products/nonexistent-id", json={"nombre": "Test"})
        assert update_response.status_code == 404
        
        # Intentar eliminar producto inexistente
        delete_response = client.delete("/api/v1/products/nonexistent-id")
        assert delete_response.status_code == 404
        
        # Crear producto con datos inválidos
        invalid_product = {
            "nombre": "",  # Nombre vacío
            "precio": -10,  # Precio negativo
            "categoria": "invalid_category"
        }
        invalid_response = client.post("/api/v1/products", json=invalid_product)
        assert invalid_response.status_code == 422
        
        # Probar validación de rango de precios en búsqueda
        invalid_search = client.get("/api/v1/products/search?precio_min=20&precio_max=10")
        assert invalid_search.status_code == 400


class TestIntegrationAuthentication:
    """Pruebas de integración para autenticación"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_auth_redis(self):
        """Mock de Redis para autenticación"""
        users_storage = {}
        sessions_storage = {}
        
        def mock_hgetall(key):
            if key.startswith("user:"):
                return users_storage.get(key, {})
            return {}
        
        def mock_hset(key, field=None, value=None, mapping=None):
            if key.startswith("user:"):
                if key not in users_storage:
                    users_storage[key] = {}
                if mapping:
                    users_storage[key].update(mapping)
                elif field and value:
                    users_storage[key][field] = value
            return True
        
        def mock_get(key):
            if key.startswith("session:"):
                return sessions_storage.get(key)
            return None
        
        def mock_set(key, value, ex=None):
            if key.startswith("session:"):
                sessions_storage[key] = value
            return True
        
        def mock_delete(key):
            if key.startswith("session:") and key in sessions_storage:
                del sessions_storage[key]
                return True
            return False
        
        with patch('main.redis_conn') as mock_conn:
            mock_conn.is_connected.return_value = True
            mock_conn.hgetall.side_effect = mock_hgetall
            mock_conn.hset.side_effect = mock_hset
            mock_conn.get.side_effect = mock_get
            mock_conn.set.side_effect = mock_set
            mock_conn.delete.side_effect = mock_delete
            yield mock_conn, users_storage, sessions_storage
    
    @pytest.mark.integration
    def test_complete_auth_flow(self, client, mock_auth_redis):
        """Probar flujo completo de autenticación"""
        mock_conn, users_storage, sessions_storage = mock_auth_redis
        
        # 1. Registrar usuario
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        register_response = client.post("/register", json=user_data)
        assert register_response.status_code == 200
        register_data = register_response.json()
        assert "token" in register_data
        token = register_data["token"]
        
        # 2. Verificar sesión válida
        verify_response = client.get("/verify-session", headers={"Authorization": f"Bearer {token}"})
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["valid"] is True
        assert verify_data["username"] == "testuser"
        
        # 3. Logout
        logout_response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
        assert logout_response.status_code == 200
        
        # 4. Verificar que la sesión ya no es válida
        verify_after_logout = client.get("/verify-session", headers={"Authorization": f"Bearer {token}"})
        assert verify_after_logout.status_code == 401
        
        # 5. Login de nuevo
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        login_response = client.post("/login", json=login_data)
        assert login_response.status_code == 200
        login_result = login_response.json()
        assert "token" in login_result
        new_token = login_result["token"]
        
        # 6. Verificar nueva sesión
        verify_new_session = client.get("/verify-session", headers={"Authorization": f"Bearer {new_token}"})
        assert verify_new_session.status_code == 200
    
    @pytest.mark.integration
    def test_duplicate_user_registration(self, client, mock_auth_redis):
        """Probar registro de usuario duplicado"""
        mock_conn, users_storage, sessions_storage = mock_auth_redis
        
        user_data = {
            "username": "duplicateuser",
            "email": "duplicate@example.com",
            "password": "password123"
        }
        
        # Primer registro (exitoso)
        first_response = client.post("/register", json=user_data)
        assert first_response.status_code == 200
        
        # Segundo registro (debe fallar)
        second_response = client.post("/register", json=user_data)
        assert second_response.status_code == 400
        assert "Usuario ya existe" in second_response.json()["detail"]
