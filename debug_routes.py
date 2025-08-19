#!/usr/bin/env python3
"""
Script de depuración para verificar el problema con las rutas
"""

from fastapi import FastAPI
from routes.products import router as products_router

app = FastAPI()

# Incluir rutas de productos
app.include_router(products_router)

# Imprimir todas las rutas registradas
print("🔍 Rutas registradas en la aplicación:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"  {list(route.methods)} {route.path}")

print("\n🎯 Verificando router de productos...")
print(f"Prefix del router: {products_router.prefix}")
print(f"Tags del router: {products_router.tags}")
print(f"Número de rutas en el router: {len(products_router.routes)}")

print("\n📋 Rutas del router de productos:")
for route in products_router.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"  {list(route.methods)} {route.path}")
