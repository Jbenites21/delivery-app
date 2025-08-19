"""
Script de prueba para la integración con Redis
Ejecuta este script para probar las funcionalidades básicas
"""

import asyncio
import httpx
import json


BASE_URL = "http://localhost:8000"


async def test_api():
    """Prueba básica de la API con Redis"""
    
    async with httpx.AsyncClient() as client:
        print("🧪 Iniciando pruebas de la API con Redis...\n")
        
        # 1. Verificar que la API esté funcionando
        print("1️⃣ Verificando estado de la API...")
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"✅ API Status: {response.json()}")
        except Exception as e:
            print(f"❌ Error conectando con la API: {e}")
            return
        
        # 2. Verificar health check
        print("\n2️⃣ Verificando health check...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            health_data = response.json()
            print(f"✅ Health Check: {health_data}")
            
            if not health_data.get("redis_connected"):
                print("⚠️ Redis no está conectado. Asegúrate de que Redis esté ejecutándose.")
                return
                
        except Exception as e:
            print(f"❌ Error en health check: {e}")
            return
        
        # 3. Probar registro de usuario
        print("\n3️⃣ Probando registro de usuario...")
        register_data = {
            "nombre": "Juan Pérez",
            "email": "juan@ejemplo.com",
            "password": "mipassword123"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/registrar", json=register_data)
            register_result = response.json()
            print(f"✅ Registro: {register_result}")
            
            if register_result.get("status"):
                token = register_result.get("token")
                print(f"🔑 Token obtenido: {token[:20]}...")
            else:
                print("❌ Fallo en el registro")
                return
                
        except Exception as e:
            print(f"❌ Error en registro: {e}")
            return
        
        # 4. Probar login
        print("\n4️⃣ Probando login...")
        login_data = {
            "email": "juan@ejemplo.com",
            "password": "mipassword123"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/login", json=login_data)
            login_result = response.json()
            print(f"✅ Login: {login_result}")
            
            if login_result.get("status"):
                login_token = login_result.get("token")
                print(f"🔑 Nuevo token: {login_token[:20]}...")
            else:
                print("❌ Fallo en el login")
                return
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return
        
        # 5. Probar obtener perfil
        print("\n5️⃣ Probando obtener perfil...")
        try:
            response = await client.get(f"{BASE_URL}/profile/{login_token}")
            profile_result = response.json()
            print(f"✅ Perfil: {json.dumps(profile_result, indent=2)}")
            
        except Exception as e:
            print(f"❌ Error obteniendo perfil: {e}")
        
        # 6. Probar estadísticas de Redis
        print("\n6️⃣ Probando estadísticas de Redis...")
        try:
            response = await client.get(f"{BASE_URL}/redis/stats")
            stats_result = response.json()
            print(f"✅ Estadísticas Redis: {json.dumps(stats_result, indent=2)}")
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
        
        # 7. Probar logout
        print("\n7️⃣ Probando logout...")
        try:
            response = await client.post(f"{BASE_URL}/logout", json={"token": login_token})
            logout_result = response.json()
            print(f"✅ Logout: {logout_result}")
            
        except Exception as e:
            print(f"❌ Error en logout: {e}")
        
        print("\n🎉 Pruebas completadas!")


if __name__ == "__main__":
    print("Para ejecutar este script:")
    print("1. Asegúrate de que Redis esté ejecutándose")
    print("2. Ejecuta la API: uvicorn main:app --reload")
    print("3. Ejecuta: python test_redis.py")
    print("\nO puedes probar manualmente con curl o un cliente HTTP como Postman")
    
    # Descomenta la siguiente línea para ejecutar las pruebas automáticamente
    # asyncio.run(test_api())
