"""
Pruebas unitarias para el router de pagos
"""

import pytest
import sys
import os
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Añadir el directorio raíz al path para las importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar el router y modelos de payment commit
from infraestructure.api.routers.payment import router, process_payment, Item, PaymentRequest, PaymentResponse


class TestPaymentModels:
    """Pruebas para los modelos de Pydantic del módulo de pagos"""
    
    def test_item_model_valid_data(self):
        """Prueba creación válida del modelo Item"""
        item_data = {
            "product_id": "prod_123",
            "quantity": 2
        }
        item = Item(**item_data)
        
        assert item.product_id == "prod_123"
        assert item.quantity == 2
    
    def test_item_model_invalid_quantity_zero(self):
        """Prueba que quantity debe ser mayor a 0"""
        with pytest.raises(ValueError):
            Item(product_id="prod_123", quantity=0)
    
    def test_item_model_invalid_quantity_negative(self):
        """Prueba que quantity no puede ser negativo"""
        with pytest.raises(ValueError):
            Item(product_id="prod_123", quantity=-1)
    
    def test_payment_request_model_valid_data(self):
        """Prueba creación válida del modelo PaymentRequest"""
        items = [
            {"product_id": "prod_1", "quantity": 2},
            {"product_id": "prod_2", "quantity": 1}
        ]
        payment_data = {
            "items": items,
            "total_amount": 150.50
        }
        payment_request = PaymentRequest(**payment_data)
        
        assert len(payment_request.items) == 2
        assert payment_request.total_amount == 150.50
        assert payment_request.items[0].product_id == "prod_1"
        assert payment_request.items[0].quantity == 2
    
    def test_payment_request_model_empty_items(self):
        """Prueba PaymentRequest con lista de items vacía"""
        payment_data = {
            "items": [],
            "total_amount": 100.0
        }
        payment_request = PaymentRequest(**payment_data)
        
        assert len(payment_request.items) == 0
        assert payment_request.total_amount == 100.0
    
    def test_payment_response_model_valid_data(self):
        """Prueba creación válida del modelo PaymentResponse"""
        response_data = {
            "message": "Pago procesado exitosamente",
            "status": "completed",
            "transaction_id": "txn_12345"
        }
        payment_response = PaymentResponse(**response_data)
        
        assert payment_response.message == "Pago procesado exitosamente"
        assert payment_response.status == "completed"
        assert payment_response.transaction_id == "txn_12345"


class TestProcessPaymentFunction:
    """Pruebas para la función process_payment"""
    
    def test_process_payment_success(self):
        """Prueba procesamiento exitoso de pago"""
        items = [Item(product_id="prod_1", quantity=2)]
        request = PaymentRequest(items=items, total_amount=100.0)
        
        response = process_payment(request)
        
        assert isinstance(response, PaymentResponse)
        assert response.message == "Pago simulado exitosamente."
        assert response.status == "completed"
        assert response.transaction_id.startswith("txn_")
    
    def test_process_payment_zero_amount(self):
        """Prueba que falla con monto total igual a cero"""
        items = [Item(product_id="prod_1", quantity=1)]
        request = PaymentRequest(items=items, total_amount=0.0)
        
        with pytest.raises(HTTPException) as exc_info:
            process_payment(request)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "El monto total debe ser mayor a cero." in str(exc_info.value.detail)
    
    def test_process_payment_negative_amount(self):
        """Prueba que falla con monto total negativo"""
        items = [Item(product_id="prod_1", quantity=1)]
        request = PaymentRequest(items=items, total_amount=-50.0)
        
        with pytest.raises(HTTPException) as exc_info:
            process_payment(request)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "El monto total debe ser mayor a cero." in str(exc_info.value.detail)
    
    def test_process_payment_multiple_items(self):
        """Prueba procesamiento con múltiples items"""
        items = [
            Item(product_id="prod_1", quantity=2),
            Item(product_id="prod_2", quantity=1),
            Item(product_id="prod_3", quantity=3)
        ]
        request = PaymentRequest(items=items, total_amount=275.99)
        
        response = process_payment(request)
        
        assert response.status == "completed"
        assert response.transaction_id.startswith("txn_")
        assert response.message == "Pago simulado exitosamente."
    
    def test_process_payment_transaction_id_consistency(self):
        """Prueba que el mismo input genera el mismo transaction_id"""
        items = [Item(product_id="prod_1", quantity=2)]
        request = PaymentRequest(items=items, total_amount=100.0)
        
        response1 = process_payment(request)
        response2 = process_payment(request)
        
        # El mismo input debería generar el mismo transaction_id
        assert response1.transaction_id == response2.transaction_id
    
    def test_process_payment_transaction_id_uniqueness(self):
        """Prueba que diferentes inputs generan diferentes transaction_ids"""
        items1 = [Item(product_id="prod_1", quantity=2)]
        request1 = PaymentRequest(items=items1, total_amount=100.0)
        
        items2 = [Item(product_id="prod_2", quantity=1)]
        request2 = PaymentRequest(items=items2, total_amount=100.0)
        
        response1 = process_payment(request1)
        response2 = process_payment(request2)
        
        # Diferentes inputs deberían generar diferentes transaction_ids
        assert response1.transaction_id != response2.transaction_id


@pytest.fixture
def app():
    """Fixture que crea una app FastAPI con el router de payments"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Fixture que crea un cliente de pruebas"""
    return TestClient(app)


class TestPaymentRouter:
    """Pruebas de integración para el router de pagos"""
    
    def test_process_payment_endpoint_success(self, client):
        """Prueba endpoint de procesamiento exitoso"""
        payload = {
            "items": [
                {"product_id": "prod_1", "quantity": 2},
                {"product_id": "prod_2", "quantity": 1}
            ],
            "total_amount": 150.75
        }
        
        response = client.post("/payment/process-payment", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Pago simulado exitosamente."
        assert data["status"] == "completed"
        assert data["transaction_id"].startswith("txn_")
    
    def test_process_payment_endpoint_zero_amount(self, client):
        """Prueba endpoint con monto total cero"""
        payload = {
            "items": [{"product_id": "prod_1", "quantity": 1}],
            "total_amount": 0.0
        }
        
        response = client.post("/payment/process-payment", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "El monto total debe ser mayor a cero." in data["detail"]
    
    def test_process_payment_endpoint_negative_amount(self, client):
        """Prueba endpoint con monto total negativo"""
        payload = {
            "items": [{"product_id": "prod_1", "quantity": 1}],
            "total_amount": -100.0
        }
        
        response = client.post("/payment/process-payment", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "El monto total debe ser mayor a cero." in data["detail"]
    
    def test_process_payment_endpoint_invalid_quantity(self, client):
        """Prueba endpoint con quantity inválida"""
        payload = {
            "items": [{"product_id": "prod_1", "quantity": 0}],
            "total_amount": 100.0
        }
        
        response = client.post("/payment/process-payment", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_process_payment_endpoint_missing_fields(self, client):
        """Prueba endpoint con campos faltantes"""
        payload = {
            "items": [{"product_id": "prod_1"}],  # Falta quantity
            "total_amount": 100.0
        }
        
        response = client.post("/payment/process-payment", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_process_payment_endpoint_empty_items(self, client):
        """Prueba endpoint con lista de items vacía"""
        payload = {
            "items": [],
            "total_amount": 100.0
        }
        
        response = client.post("/payment/process-payment", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
    
    def test_process_payment_endpoint_invalid_json(self, client):
        """Prueba endpoint con JSON inválido"""
        response = client.post("/payment/process-payment", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        
        assert response.status_code == 422
    
    def test_process_payment_endpoint_missing_total_amount(self, client):
        """Prueba endpoint sin total_amount"""
        payload = {
            "items": [{"product_id": "prod_1", "quantity": 1}]
            # Falta total_amount
        }
        
        response = client.post("/payment/process-payment", json=payload)
        
        assert response.status_code == 422  # Validation error
        
    def test_process_payment_endpoint_large_amount(self, client):
        """Prueba endpoint con monto muy grande"""
        payload = {
            "items": [{"product_id": "prod_1", "quantity": 1}],
            "total_amount": 999999999.99
        }
        
        response = client.post("/payment/process-payment", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
