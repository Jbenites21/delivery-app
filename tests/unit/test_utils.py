"""
Pruebas unitarias básicas para funciones de utilidad.
"""

import pytest
from main import generate_token, hash_password, verify_password


def test_generate_token_basic():
    """El token debe ser una cadena de 64 caracteres"""
    token = generate_token()
    assert isinstance(token, str)
    assert len(token) == 64


def test_hash_password_basic():
    """Verificar que las contraseñas se hashean correctamente"""
    password = "password123"
    hashed = hash_password(password)
    
    assert isinstance(hashed, str)
    assert len(hashed) == 64  # SHA256 produce 64 caracteres hex
    assert hashed != password  # El hash debe ser diferente a la contraseña original


def test_verify_password_correct():
    """Verificar contraseña correcta"""
    password = "password123"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Verificar contraseña incorrecta"""
    password = "password123"
    wrong_password = "wrongpassword"
    hashed = hash_password(password)
    
    assert verify_password(wrong_password, hashed) is False
