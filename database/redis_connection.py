import redis
import json
import os
import time
from typing import Optional, Any
from pydantic import BaseModel


class RedisConnection:
    """Clase para manejar la conexión y operaciones con Redis"""
    
    def __init__(self, host: str = None, port: int = None, db: int = None, password: str = None):
        self.redis_client = None
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port or int(os.getenv('REDIS_PORT', 6379))
        self.db = db or int(os.getenv('REDIS_DB', 0))
        self.password = password or os.getenv('REDIS_PASSWORD', None)
        self.connect()
    
    def connect(self):
        """Establece la conexión con Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,  # Para obtener strings en lugar de bytes
                socket_connect_timeout=10,  # Aumentado para contenedores
                socket_timeout=10,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Verificar la conexión
            self.redis_client.ping()
            print(f"✅ Conexión exitosa con Redis en {self.host}:{self.port}")
            
        except redis.ConnectionError as e:
            print(f"❌ Error de conexión con Redis: {e}")
            print(f"   Host: {self.host}, Puerto: {self.port}")
            self.redis_client = None
        except Exception as e:
            print(f"❌ Error inesperado con Redis: {e}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Verifica si hay conexión activa con Redis"""
        if self.redis_client is None:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def set_data(self, key: str, value: Any, expire_time: Optional[int] = None) -> bool:
        """
        Almacena datos en Redis
        
        Args:
            key: Clave para almacenar
            value: Valor a almacenar (se serializa a JSON si es un objeto)
            expire_time: Tiempo de expiración en segundos
            
        Returns:
            True si se almacenó correctamente, False en caso contrario
        """
        if not self.is_connected():
            return False
        
        try:
            # Si el valor es un modelo de Pydantic o un dict, lo convertimos a JSON
            if isinstance(value, BaseModel):
                value = value.model_dump()
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            result = self.redis_client.set(key, value)
            
            # Establecer tiempo de expiración si se proporciona
            if expire_time and result:
                self.redis_client.expire(key, expire_time)
            
            return result
        except Exception as e:
            print(f"Error al guardar en Redis: {e}")
            return False
    
    def get_data(self, key: str) -> Optional[Any]:
        """
        Recupera datos de Redis
        
        Args:
            key: Clave a buscar
            
        Returns:
            Los datos almacenados o None si no existen
        """
        if not self.is_connected():
            return None
        
        try:
            data = self.redis_client.get(key)
            if data is None:
                return None
            
            # Intentar deserializar JSON
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                # Si no es JSON válido, retornar como string
                return data
                
        except Exception as e:
            print(f"Error al obtener datos de Redis: {e}")
            return None
    
    def delete_data(self, key: str) -> bool:
        """
        Elimina una clave de Redis
        
        Args:
            key: Clave a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        if not self.is_connected():
            return False
        
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            print(f"Error al eliminar de Redis: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe en Redis
        
        Args:
            key: Clave a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        if not self.is_connected():
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"Error al verificar existencia en Redis: {e}")
            return False
    
    def set_user_session(self, user_email: str, token: str, expire_time: int = 3600) -> bool:
        """
        Almacena una sesión de usuario con token
        
        Args:
            user_email: Email del usuario
            token: Token de sesión
            expire_time: Tiempo de expiración en segundos (default: 1 hora)
            
        Returns:
            True si se almacenó correctamente
        """
        session_key = f"session:{token}"
        user_data = {
            "email": user_email,
            "created_at": str(int(time.time()))
        }
        return self.set_data(session_key, user_data, expire_time)
    
    def get_user_session(self, token: str) -> Optional[dict]:
        """
        Recupera información de sesión por token
        
        Args:
            token: Token de sesión
            
        Returns:
            Datos del usuario o None si no existe
        """
        session_key = f"session:{token}"
        return self.get_data(session_key)
    
    def invalidate_session(self, token: str) -> bool:
        """
        Invalida una sesión eliminando el token
        
        Args:
            token: Token a invalidar
            
        Returns:
            True si se invalidó correctamente
        """
        session_key = f"session:{token}"
        return self.delete_data(session_key)
    
    def close_connection(self):
        """Cierra la conexión con Redis"""
        if self.redis_client:
            self.redis_client.close()
            print("🔌 Conexión con Redis cerrada")


# Instancia global de Redis
redis_conn = RedisConnection()
