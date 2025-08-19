"""
Configuración específica de fixtures para las pruebas de payment
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import sys
import os

# Añadir el directorio raíz al path para las importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from infraestructure.api.routers.payment import router


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
