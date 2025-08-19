"""
Script de prueba para el módulo de productos
Ejecuta este script para probar las funcionalidades de productos y restaurantes
"""

import asyncio
import httpx
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000/api/v1"


async def test_products_api():
    """Prueba completa de la API de productos"""
    
    async with httpx.AsyncClient() as client:
        print("🧪 Iniciando pruebas del módulo de productos...\n")
        
        # Variables para almacenar IDs
        restaurant_id = None
        product_id = None
        
        # 1. Crear un restaurante
        print("1️⃣ Creando restaurante...")
        restaurant_data = {
            "nombre": "Pizza Express",
            "descripcion": "Las mejores pizzas de la ciudad",
            "direccion": "Av. Principal 123, Centro",
            "telefono": "+593-99-123-4567",
            "email": "info@pizzaexpress.com",
            "owner_email": "juan@ejemplo.com"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/restaurants", json=restaurant_data)
            if response.status_code == 200:
                result = response.json()
                if result["status"]:
                    restaurant_id = result["restaurant"]["id"]
                    print(f"✅ Restaurante creado: {result['restaurant']['nombre']} (ID: {restaurant_id})")
                else:
                    print(f"❌ Error creando restaurante: {result['message']}")
                    return
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error creando restaurante: {e}")
            return
        
        # 2. Obtener información del restaurante
        print(f"\n2️⃣ Obteniendo información del restaurante...")
        try:
            response = await client.get(f"{BASE_URL}/restaurants/{restaurant_id}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Restaurante encontrado: {result['restaurant']['nombre']}")
            else:
                print(f"❌ Error obteniendo restaurante: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 3. Crear productos
        print(f"\n3️⃣ Creando productos...")
        products_data = [
            {
                "nombre": "Pizza Margherita",
                "descripcion": "Pizza clásica con tomate, mozzarella y albahaca",
                "precio": 12.99,
                "categoria": "pizza",
                "imagen_url": "https://example.com/pizza-margherita.jpg",
                "disponible": True,
                "tiempo_preparacion": 20,
                "restaurante_id": restaurant_id
            },
            {
                "nombre": "Pizza Pepperoni",
                "descripcion": "Pizza con pepperoni y queso mozzarella",
                "precio": 14.99,
                "categoria": "pizza",
                "disponible": True,
                "tiempo_preparacion": 25,
                "restaurante_id": restaurant_id
            },
            {
                "nombre": "Coca Cola 500ml",
                "descripcion": "Bebida gaseosa",
                "precio": 2.50,
                "categoria": "bebidas",
                "disponible": True,
                "restaurante_id": restaurant_id
            }
        ]
        
        created_products = []
        for i, product_data in enumerate(products_data, 1):
            try:
                response = await client.post(f"{BASE_URL}/products", json=product_data)
                if response.status_code == 200:
                    result = response.json()
                    if result["status"]:
                        created_products.append(result["product"])
                        if i == 1:  # Guardar ID del primer producto para pruebas
                            product_id = result["product"]["id"]
                        print(f"✅ Producto {i} creado: {result['product']['nombre']} (${result['product']['precio']})")
                    else:
                        print(f"❌ Error creando producto {i}: {result['message']}")
                else:
                    print(f"❌ Error HTTP {response.status_code} en producto {i}: {response.text}")
            except Exception as e:
                print(f"❌ Error creando producto {i}: {e}")
        
        # 4. Buscar productos
        print(f"\n4️⃣ Buscando productos...")
        try:
            # Buscar todos los productos
            response = await client.get(f"{BASE_URL}/products")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Búsqueda general: {len(result['products'])} productos encontrados")
            
            # Buscar por categoría
            response = await client.get(f"{BASE_URL}/products?categoria=pizza")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Búsqueda por categoría 'pizza': {len(result['products'])} productos")
            
            # Buscar por rango de precio
            response = await client.get(f"{BASE_URL}/products?precio_min=10&precio_max=15")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Búsqueda por precio ($10-$15): {len(result['products'])} productos")
            
            # Buscar por término
            response = await client.get(f"{BASE_URL}/products?search_term=pizza")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Búsqueda por término 'pizza': {len(result['products'])} productos")
                
        except Exception as e:
            print(f"❌ Error en búsquedas: {e}")
        
        # 5. Obtener productos del restaurante
        print(f"\n5️⃣ Obteniendo productos del restaurante...")
        try:
            response = await client.get(f"{BASE_URL}/restaurants/{restaurant_id}/products")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Productos del restaurante: {len(result['products'])} productos")
                for product in result['products']:
                    print(f"   - {product['nombre']}: ${product['precio']}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 6. Obtener productos por categoría
        print(f"\n6️⃣ Obteniendo productos por categoría...")
        try:
            response = await client.get(f"{BASE_URL}/categories/pizza/products")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Productos de categoría 'pizza': {len(result['products'])} productos")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 7. Actualizar producto
        if product_id:
            print(f"\n7️⃣ Actualizando producto...")
            update_data = {
                "precio": 13.99,
                "descripcion": "Pizza clásica con tomate, mozzarella fresca y albahaca - NUEVA RECETA"
            }
            try:
                response = await client.put(f"{BASE_URL}/products/{product_id}", json=update_data)
                if response.status_code == 200:
                    result = response.json()
                    if result["status"]:
                        print(f"✅ Producto actualizado: {result['product']['nombre']} - ${result['product']['precio']}")
                    else:
                        print(f"❌ Error actualizando: {result['message']}")
                else:
                    print(f"❌ Error HTTP: {response.text}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # 8. Obtener categorías
        print(f"\n8️⃣ Obteniendo categorías disponibles...")
        try:
            response = await client.get(f"{BASE_URL}/categories")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Categorías disponibles:")
                for category in result['categories']:
                    print(f"   - {category['value']}: {category['name']}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 9. Obtener producto específico
        if product_id:
            print(f"\n9️⃣ Obteniendo producto específico...")
            try:
                response = await client.get(f"{BASE_URL}/products/{product_id}")
                if response.status_code == 200:
                    result = response.json()
                    product = result['product']
                    print(f"✅ Producto encontrado:")
                    print(f"   - Nombre: {product['nombre']}")
                    print(f"   - Precio: ${product['precio']}")
                    print(f"   - Categoría: {product['categoria']}")
                    print(f"   - Disponible: {product['disponible']}")
                    print(f"   - Tiempo preparación: {product['tiempo_preparacion']} min")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # 10. Obtener lista de restaurantes
        print(f"\n🔟 Obteniendo lista de restaurantes...")
        try:
            response = await client.get(f"{BASE_URL}/restaurants")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Restaurantes encontrados: {len(result['restaurants'])}")
                for restaurant in result['restaurants']:
                    print(f"   - {restaurant['nombre']} ({restaurant['direccion']})")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n🎉 Pruebas del módulo de productos completadas!")
        print("\n📊 Resumen de endpoints probados:")
        print("   ✅ POST /api/v1/restaurants - Crear restaurante")
        print("   ✅ GET  /api/v1/restaurants/{id} - Obtener restaurante")
        print("   ✅ GET  /api/v1/restaurants - Listar restaurantes")
        print("   ✅ POST /api/v1/products - Crear producto")
        print("   ✅ GET  /api/v1/products/{id} - Obtener producto")
        print("   ✅ PUT  /api/v1/products/{id} - Actualizar producto")
        print("   ✅ GET  /api/v1/products - Buscar productos (con filtros)")
        print("   ✅ GET  /api/v1/restaurants/{id}/products - Productos por restaurante")
        print("   ✅ GET  /api/v1/categories/{category}/products - Productos por categoría")
        print("   ✅ GET  /api/v1/categories - Listar categorías")


if __name__ == "__main__":
    print("Para ejecutar este script:")
    print("1. Asegúrate de que la API esté ejecutándose: docker-compose up -d")
    print("2. Ejecuta: python test_products.py")
    print("\nO puedes usar la documentación automática en: http://localhost:8000/docs")
    
    # Descomenta la siguiente línea para ejecutar las pruebas automáticamente
    # asyncio.run(test_products_api())
