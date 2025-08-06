from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import secrets
import hashlib
import time
from models import usermodels
from database import redis_conn
from routes.products import router as products_router

app = FastAPI(
    title="Delivery App API",
    description="API para aplicación de delivery con autenticación usando Redis",
    version="1.0.0"
)

# Incluir rutas de productos
app.include_router(products_router)


def generate_token() -> str:
    """Genera un token único para la sesión"""
    return secrets.token_hex(32)


def hash_password(password: str) -> str:
    """Crea un hash simple de la contraseña (en producción usar bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verifica si la contraseña coincide con el hash"""
    return hash_password(password) == hashed


async def check_redis_connection():
    """Middleware para verificar la conexión con Redis"""
    if not redis_conn.is_connected():
        # Intentar reconectar
        print("🔄 Intentando reconectar con Redis...")
        redis_conn.connect()
        if not redis_conn.is_connected():
            raise HTTPException(
                status_code=503, 
                detail="Servicio no disponible: Error de conexión con Redis"
            )


@app.get("/")
async def root():
    """Endpoint de prueba"""
    return {"message": "Delivery App API", "status": "running", "redis_connected": redis_conn.is_connected()}


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la aplicación"""
    return {
        "status": "healthy",
        "redis_connected": redis_conn.is_connected(),
        "timestamp": int(time.time())
    }



@app.post("/login", response_model=usermodels.LoginResponse)
async def login(user: usermodels.UserLogin):
    """
    Endpoint para iniciar sesión
    
    - Verifica si el usuario existe en Redis
    - Valida la contraseña
    - Genera un token de sesión
    - Almacena la sesión en Redis
    """
    await check_redis_connection()
    
    try:
        # Buscar usuario registrado
        user_key = f"user:{user.email}"
        stored_user = redis_conn.get_data(user_key)
        
        if not stored_user:
            return usermodels.LoginResponse(
                status=False,
                message="Usuario no encontrado. Por favor regístrate primero."
            )
        
        # Verificar contraseña
        if not verify_password(user.password, stored_user["password_hash"]):
            return usermodels.LoginResponse(
                status=False,
                message="Contraseña incorrecta"
            )
        
        # Generar token de sesión
        token = generate_token()
        
        # Almacenar sesión en Redis (expira en 24 horas)
        session_data = {
            "email": user.email,
            "nombre": stored_user["nombre"],
            "created_at": str(int(time.time()))
        }
        
        session_success = redis_conn.set_data(f"session:{token}", session_data, 86400)
        
        if not session_success:
            raise HTTPException(status_code=500, detail="Error al crear la sesión")
        
        print(f"✅ Usuario {user.email} inició sesión exitosamente")
        
        return usermodels.LoginResponse(
            status=True,
            message="Login exitoso",
            token=token,
            username=stored_user["nombre"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en login: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.post("/registrar", response_model=usermodels.RegisterResponse)
async def registrar(user: usermodels.UserRegister):
    """
    Endpoint para registrar un nuevo usuario
    
    - Verifica que el email no esté registrado
    - Hashea la contraseña
    - Almacena el usuario en Redis
    - Genera un token de sesión
    """
    await check_redis_connection()
    
    try:
        # Verificar si el usuario ya existe
        user_key = f"user:{user.email}"
        
        if redis_conn.exists(user_key):
            return usermodels.RegisterResponse(
                status=False,
                message="El usuario ya está registrado"
            )
        
        # Hashear la contraseña
        password_hash = hash_password(user.password)
        
        # Datos del usuario para almacenar
        user_data = {
            "nombre": user.nombre,
            "email": user.email,
            "password_hash": password_hash,
            "created_at": str(int(time.time()))
        }
        
        # Almacenar usuario en Redis
        user_success = redis_conn.set_data(user_key, user_data)
        
        if not user_success:
            raise HTTPException(status_code=500, detail="Error al registrar el usuario")
        
        # Generar token de sesión
        token = generate_token()
        
        # Almacenar sesión en Redis (expira en 24 horas)
        session_data = {
            "email": user.email,
            "nombre": user.nombre,
            "created_at": str(int(time.time()))
        }
        
        session_success = redis_conn.set_data(f"session:{token}", session_data, 86400)
        
        if not session_success:
            # Si falla la sesión, eliminar el usuario registrado
            redis_conn.delete_data(user_key)
            raise HTTPException(status_code=500, detail="Error al crear la sesión")
        
        print(f"✅ Usuario {user.nombre} registrado exitosamente con email {user.email}")
        
        return usermodels.RegisterResponse(
            status=True,
            message="Registro exitoso",
            token=token,
            username=user.nombre
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# Endpoint alternativo para compatibilidad (registar sin 'r')
@app.post("/registar", response_model=usermodels.RegisterResponse)
async def registar_alt(user: usermodels.UserRegister):
    """Endpoint alternativo para registro (redirige al endpoint correcto)"""
    return await registrar(user)


@app.post("/logout")
async def logout(token: str):
    """
    Endpoint para cerrar sesión
    
    - Invalida el token de sesión en Redis
    """
    await check_redis_connection()
    
    try:
        # Verificar que la sesión existe
        session_data = redis_conn.get_data(f"session:{token}")
        
        if not session_data:
            return {"status": False, "message": "Sesión no válida"}
        
        # Invalidar la sesión
        success = redis_conn.delete_data(f"session:{token}")
        
        if success:
            print(f"✅ Sesión cerrada para usuario: {session_data.get('email', 'unknown')}")
            return {"status": True, "message": "Sesión cerrada exitosamente"}
        else:
            return {"status": False, "message": "Error al cerrar sesión"}
            
    except Exception as e:
        print(f"❌ Error en logout: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.get("/profile/{token}")
async def get_profile(token: str):
    """
    Endpoint para obtener información del perfil del usuario
    
    - Verifica el token de sesión
    - Retorna información del usuario
    """
    await check_redis_connection()
    
    try:
        # Verificar sesión
        session_data = redis_conn.get_data(f"session:{token}")
        
        if not session_data:
            raise HTTPException(status_code=401, detail="Token no válido o expirado")
        
        # Obtener datos completos del usuario
        user_data = redis_conn.get_data(f"user:{session_data['email']}")
        
        if not user_data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Retornar información del perfil (sin el hash de la contraseña)
        profile_data = {
            "nombre": user_data["nombre"],
            "email": user_data["email"],
            "created_at": user_data["created_at"],
            "session_created": session_data["created_at"]
        }
        
        return {"status": True, "profile": profile_data}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al obtener perfil: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.get("/redis/stats")
async def redis_stats():
    """
    Endpoint para obtener estadísticas de Redis (solo para desarrollo)
    """
    await check_redis_connection()
    
    try:
        # Obtener información básica de Redis
        info = redis_conn.redis_client.info()
        
        # Contar usuarios y sesiones
        all_keys = redis_conn.redis_client.keys("*")
        user_keys = [k for k in all_keys if k.startswith("user:")]
        session_keys = [k for k in all_keys if k.startswith("session:")]
        
        stats = {
            "redis_version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory_human": info.get("used_memory_human"),
            "total_users": len(user_keys),
            "active_sessions": len(session_keys),
            "total_keys": len(all_keys)
        }
        
        return {"status": True, "stats": stats}
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")