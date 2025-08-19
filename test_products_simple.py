#!/usr/bin/env python3
"""
Script de prueba para el módulo de productos simplificado
Solo funcionalidades CRUD básicas
"""

import requests
import json
import time
from typing import List, Dict

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class ProductTester:
    def __init__(self):
        self.created_products = []
        
    def test_create_product(self):
        """Probar creación de productos"""
        print("\n🧪 Probando creación de productos...")
        
        test_products = [
            {
                "nombre": "Pizza Margherita",
                "descripcion": "Pizza clásica con tomate, mozzarella y albahaca",
                "precio": 12.99,
                "categoria": "pizzas",
                "imagen_url": "https://ejemplo.com/pizza-margherita.jpg",
                "disponible": True,
                "tiempo_preparacion": 20
            },
            {
                "nombre": "Hamburguesa BBQ",
                "descripcion": "Hamburguesa con carne, queso, cebolla caramelizada y salsa BBQ",
                "precio": 15.50,
                "categoria": "hamburguesas",
                "imagen_url": "https://ejemplo.com/burger-bbq.jpg",
                "disponible": True,
                "tiempo_preparacion": 15
            },
            {
                "nombre": "Ensalada César",
                "descripcion": "Ensalada con lechuga, crutones, queso parmesano y aderezo césar",
                "precio": 8.75,
                "categoria": "ensaladas",
                "imagen_url": "https://ejemplo.com/ensalada-cesar.jpg",
                "disponible": True,
                "tiempo_preparacion": 5
            },
            {
                "nombre": "Tacos de Pollo",
                "descripcion": "3 tacos de pollo con guacamole y pico de gallo",
                "precio": 11.25,
                "categoria": "mexicana",
                "imagen_url": "https://ejemplo.com/tacos-pollo.jpg",
                "disponible": False,
                "tiempo_preparacion": 12
            }
        ]
        
        for product_data in test_products:
            try:
                response = requests.post(
                    f"{API_BASE}/products",
                    json=product_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    product_id = result["product"]["id"]
                    self.created_products.append(product_id)
                    print(f"✅ Producto creado: {product_data['nombre']} (ID: {product_id})")
                else:
                    print(f"❌ Error creando producto {product_data['nombre']}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error de conexión creando producto: {e}")
        
        print(f"\n📊 Productos creados: {len(self.created_products)}")
    
    def test_get_all_products(self):
        """Probar obtener todos los productos"""
        print("\n🧪 Probando obtener todos los productos...")
        
        try:
            response = requests.get(f"{API_BASE}/products")
            
            if response.status_code == 200:
                result = response.json()
                products = result["products"]
                print(f"✅ Obtenidos {len(products)} productos")
                
                for product in products[:3]:  # Mostrar solo los primeros 3
                    print(f"   - {product['nombre']}: ${product['precio']}")
                    
            else:
                print(f"❌ Error obteniendo productos: {response.text}")
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
    
    def test_get_product_by_id(self):
        """Probar obtener producto por ID"""
        print("\n🧪 Probando obtener producto por ID...")
        
        if not self.created_products:
            print("⚠️ No hay productos creados para probar")
            return
        
        product_id = self.created_products[0]
        
        try:
            response = requests.get(f"{API_BASE}/products/{product_id}")
            
            if response.status_code == 200:
                result = response.json()
                product = result["product"]
                print(f"✅ Producto obtenido: {product['nombre']}")
                print(f"   - Precio: ${product['precio']}")
                print(f"   - Categoría: {product['categoria']}")
                print(f"   - Disponible: {product['disponible']}")
            else:
                print(f"❌ Error obteniendo producto: {response.text}")
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
    
    def test_update_product(self):
        """Probar actualización de productos"""
        print("\n🧪 Probando actualización de productos...")
        
        if not self.created_products:
            print("⚠️ No hay productos creados para probar")
            return
        
        product_id = self.created_products[0]
        update_data = {
            "precio": 14.99,
            "descripcion": "Pizza Margherita mejorada con ingredientes premium",
            "disponible": True
        }
        
        try:
            response = requests.put(
                f"{API_BASE}/products/{product_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                product = result["product"]
                print(f"✅ Producto actualizado: {product['nombre']}")
                print(f"   - Nuevo precio: ${product['precio']}")
                print(f"   - Nueva descripción: {product['descripcion']}")
            else:
                print(f"❌ Error actualizando producto: {response.text}")
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
    
    def test_search_products(self):
        """Probar búsqueda de productos"""
        print("\n🧪 Probando búsqueda de productos...")
        
        test_searches = [
            {"search_term": "pizza", "description": "por término 'pizza'"},
            {"categoria": "hamburguesas", "description": "por categoría 'hamburguesas'"},
            {"precio_min": 10, "precio_max": 15, "description": "por rango de precio $10-$15"},
            {"disponible": True, "description": "solo productos disponibles"}
        ]
        
        for search in test_searches:
            try:
                params = {k: v for k, v in search.items() if k != "description"}
                response = requests.get(f"{API_BASE}/products/search", params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    products = result["products"]
                    print(f"✅ Búsqueda {search['description']}: {len(products)} resultados")
                    
                    for product in products[:2]:  # Mostrar solo los primeros 2
                        print(f"   - {product['nombre']}: ${product['precio']}")
                        
                else:
                    print(f"❌ Error en búsqueda {search['description']}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error de conexión en búsqueda: {e}")
    
    def test_get_products_by_category(self):
        """Probar obtener productos por categoría"""
        print("\n🧪 Probando obtener productos por categoría...")
        
        categories = ["pizzas", "hamburguesas", "ensaladas"]
        
        for category in categories:
            try:
                response = requests.get(f"{API_BASE}/products/category/{category}")
                
                if response.status_code == 200:
                    result = response.json()
                    products = result["products"]
                    print(f"✅ Categoría '{category}': {len(products)} productos")
                    
                    for product in products:
                        print(f"   - {product['nombre']}: ${product['precio']}")
                        
                else:
                    print(f"❌ Error obteniendo productos de categoría {category}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error de conexión: {e}")
    
    def test_get_categories(self):
        """Probar obtener categorías disponibles"""
        print("\n🧪 Probando obtener categorías...")
        
        try:
            response = requests.get(f"{API_BASE}/categories")
            
            if response.status_code == 200:
                result = response.json()
                categories = result["categories"]
                print(f"✅ Categorías disponibles: {len(categories)}")
                
                for category in categories:
                    print(f"   - {category['name']} ({category['value']})")
                    
            else:
                print(f"❌ Error obteniendo categorías: {response.text}")
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
    
    def test_get_product_stats(self):
        """Probar obtener estadísticas de productos"""
        print("\n🧪 Probando obtener estadísticas...")
        
        try:
            response = requests.get(f"{API_BASE}/products/stats")
            
            if response.status_code == 200:
                result = response.json()
                stats = result["stats"]
                print(f"✅ Estadísticas obtenidas:")
                print(f"   - Total productos: {stats['total_products']}")
                print(f"   - Productos disponibles: {stats['available_products']}")
                print(f"   - Productos no disponibles: {stats['unavailable_products']}")
                print("   - Por categoría:")
                for cat, count in stats['products_by_category'].items():
                    print(f"     • {cat}: {count}")
                    
            else:
                print(f"❌ Error obteniendo estadísticas: {response.text}")
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
    
    def test_delete_product(self):
        """Probar eliminación de productos"""
        print("\n🧪 Probando eliminación de productos...")
        
        if len(self.created_products) < 2:
            print("⚠️ No hay suficientes productos para probar eliminación")
            return
        
        # Eliminar el último producto creado
        product_id = self.created_products.pop()
        
        try:
            response = requests.delete(f"{API_BASE}/products/{product_id}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Producto eliminado: {result['message']}")
                
                # Verificar que realmente se eliminó
                verify_response = requests.get(f"{API_BASE}/products/{product_id}")
                if verify_response.status_code == 404:
                    print("✅ Verificación: El producto ya no existe")
                else:
                    print("⚠️ Advertencia: El producto aún existe")
                    
            else:
                print(f"❌ Error eliminando producto: {response.text}")
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Iniciando pruebas del módulo de productos simplificado...")
        print("=" * 60)
        
        # Verificar que el servidor esté ejecutándose
        try:
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code != 200:
                print("❌ El servidor no está respondiendo. ¿Está ejecutándose?")
                return
        except:
            print("❌ No se puede conectar al servidor. ¿Está ejecutándose en http://localhost:8000?")
            return
        
        # Ejecutar pruebas en orden
        self.test_create_product()
        time.sleep(1)
        
        self.test_get_all_products()
        time.sleep(1)
        
        self.test_get_product_by_id()
        time.sleep(1)
        
        self.test_update_product()
        time.sleep(1)
        
        self.test_search_products()
        time.sleep(1)
        
        self.test_get_products_by_category()
        time.sleep(1)
        
        self.test_get_categories()
        time.sleep(1)
        
        self.test_get_product_stats()
        time.sleep(1)
        
        self.test_delete_product()
        
        print("\n" + "=" * 60)
        print("🎉 Pruebas completadas!")
        print(f"📊 Productos restantes creados: {len(self.created_products)}")


if __name__ == "__main__":
    tester = ProductTester()
    tester.run_all_tests()
