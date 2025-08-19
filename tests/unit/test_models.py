"""
Pruebas unitarias para modelos Pydantic del delivery app.
"""

import pytest
from pydantic import ValidationError
from models.productmodels import (
    ProductCategory, ProductCreate, ProductUpdate, 
    Product, ProductSearchFilter
)


def test_product_categories_exist():
    """Verificar que todas las categorías esperadas estén definidas"""
    expected_categories = [
        "comida_rapida", "pizzas", "hamburguesas", "pollo", 
        "mariscos", "bebidas", "postres", "ensaladas", 
        "vegetariano", "mexicana", "otros"
    ]
    
    actual_categories = [category.value for category in ProductCategory]
    
    for expected in expected_categories:
        assert expected in actual_categories


def test_category_string_representation():
    """Verificar la representación string de las categorías"""
    assert ProductCategory.pizzas.value == "pizzas"
    assert ProductCategory.hamburguesas.value == "hamburguesas"
    assert ProductCategory.bebidas.value == "bebidas"


def test_valid_product_creation():
    """Crear un producto válido"""
    product_data = {
        "nombre": "Pizza Margherita",
        "descripcion": "Pizza clásica con tomate, mozzarella y albahaca",
        "precio": 15.99,
        "categoria": ProductCategory.pizzas,
        "imagen_url": "https://example.com/pizza.jpg",
        "disponible": True,
        "tiempo_preparacion": 25
    }
    
    product = ProductCreate(**product_data)
    assert product.nombre == "Pizza Margherita"
    assert product.precio == 15.99
    assert product.categoria == ProductCategory.pizzas
    assert product.disponible is True


def test_invalid_price_negative():
    """La validación debe fallar con precio negativo"""
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            nombre="Pizza Margherita",
            precio=-5.0,
            categoria=ProductCategory.pizzas
        )
    assert "greater than 0" in str(exc_info.value)


def test_invalid_price_zero():
    """La validación debe fallar con precio cero"""
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            nombre="Pizza Margherita",
            precio=0.0,
            categoria=ProductCategory.pizzas
        )
    assert "greater than 0" in str(exc_info.value)


def test_empty_name():
    """La validación debe fallar con nombre vacío"""
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            nombre="",
            precio=15.99,
            categoria=ProductCategory.pizzas
        )
    assert "at least 2 characters" in str(exc_info.value)


def test_short_name():
    """La validación debe fallar con nombre muy corto"""
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            nombre="A",
            precio=15.99,
            categoria=ProductCategory.pizzas
        )
    assert "at least 2 characters" in str(exc_info.value)


def test_optional_fields():
    """Los campos opcionales funcionan correctamente"""
    product = ProductCreate(
        nombre="Pizza Margherita",
        precio=15.99,
        categoria=ProductCategory.pizzas
    )
    assert product.imagen_url is None
    assert product.disponible is True  # Valor por defecto


def test_product_update_optional_fields():
    """Todos los campos deben ser opcionales en ProductUpdate"""
    update = ProductUpdate()
    assert update.nombre is None
    assert update.precio is None
    assert update.categoria is None


def test_partial_update():
    """Permitir actualizaciones parciales"""
    update = ProductUpdate(
        precio=20.99,
        disponible=False
    )
    assert update.precio == 20.99
    assert update.disponible is False
    assert update.nombre is None


def test_invalid_price_in_update():
    """La validación debe fallar con precio inválido en actualización"""
    with pytest.raises(ValidationError):
        ProductUpdate(precio=-5.0)


def test_complete_product():
    """Crear un producto completo con todos los campos"""
    product_data = {
        "id": "test-product-id",
        "nombre": "Pizza Margherita",
        "descripcion": "Pizza clásica con tomate, mozzarella y albahaca",
        "precio": 15.99,
        "categoria": ProductCategory.pizzas,
        "imagen_url": "https://example.com/pizza.jpg",
        "disponible": True,
        "tiempo_preparacion": 25,
        "created_at": "1640995200",
        "updated_at": "1640995300"
    }
    
    product = Product(**product_data)
    assert product.id == "test-product-id"
    assert product.nombre == "Pizza Margherita"
    assert product.categoria == ProductCategory.pizzas
    assert product.created_at == "1640995200"


def test_product_serialization():
    """Verificar que el producto se puede serializar a dict"""
    product = Product(
        id="test-id",
        nombre="Pizza Margherita",
        precio=15.99,
        categoria=ProductCategory.pizzas,
        created_at="1640995200"
    )
    
    product_dict = product.model_dump()
    assert product_dict["id"] == "test-id"
    assert product_dict["categoria"] == "pizzas"


def test_search_filter_empty():
    """Crear filtro vacío"""
    filter_obj = ProductSearchFilter()
    assert filter_obj.categoria is None
    assert filter_obj.precio_min is None
    assert filter_obj.precio_max is None


def test_search_filter_with_term():
    """Filtro con término de búsqueda"""
    filter_obj = ProductSearchFilter(search_term="pizza")
    assert filter_obj.search_term == "pizza"


def test_search_filter_with_category():
    """Filtro con categoría específica"""
    filter_obj = ProductSearchFilter(categoria=ProductCategory.pizzas)
    assert filter_obj.categoria == ProductCategory.pizzas


def test_search_filter_with_price_range():
    """Filtro con rango de precios"""
    filter_obj = ProductSearchFilter(precio_min=10.0, precio_max=25.0)
    assert filter_obj.precio_min == 10.0
    assert filter_obj.precio_max == 25.0


def test_search_filter_invalid_prices():
    """La validación debe fallar con precios negativos"""
    with pytest.raises(ValidationError):
        ProductSearchFilter(precio_min=-5.0)
    
    with pytest.raises(ValidationError):
        ProductSearchFilter(precio_max=-10.0)


def test_search_filter_with_availability():
    """Filtro con disponibilidad"""
    filter_obj = ProductSearchFilter(disponible=True)
    assert filter_obj.disponible is True
