"""
Pruebas unitarias para la conexión Redis
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import redis

from database.redis_connection import RedisConnection


class TestRedisConnection:
    """Pruebas para la clase RedisConnection"""
    
    @pytest.fixture
    def redis_conn(self):
        """Instancia de RedisConnection para pruebas"""
        return RedisConnection()
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock del cliente Redis"""
        mock_client = Mock(spec=redis.Redis)
        mock_client.ping.return_value = True
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.delete.return_value = 1
        mock_client.exists.return_value = 0
        mock_client.hgetall.return_value = {}
        mock_client.hset.return_value = 1
        mock_client.hdel.return_value = 1
        mock_client.keys.return_value = []
        mock_client.scan_iter.return_value = iter([])
        return mock_client
    
    def test_connect_success(self, redis_conn, mock_redis_client):
        """Conexión exitosa a Redis"""
        with patch('redis.Redis', return_value=mock_redis_client):
            result = redis_conn.connect()
            
            assert result is True
            assert redis_conn.client is not None
            assert redis_conn.is_connected() is True
            mock_redis_client.ping.assert_called_once()
    
    def test_connect_failure(self, redis_conn):
        """Fallo en la conexión a Redis"""
        with patch('redis.Redis') as mock_redis:
            mock_redis.side_effect = redis.ConnectionError("Connection failed")
            
            result = redis_conn.connect()
            
            assert result is False
            assert redis_conn.client is None
            assert redis_conn.is_connected() is False
    
    def test_connect_ping_failure(self, redis_conn, mock_redis_client):
        """Fallo en el ping después de la conexión"""
        mock_redis_client.ping.side_effect = redis.ConnectionError("Ping failed")
        
        with patch('redis.Redis', return_value=mock_redis_client):
            result = redis_conn.connect()
            
            assert result is False
            assert redis_conn.client is None
            assert redis_conn.is_connected() is False
    
    def test_disconnect(self, redis_conn, mock_redis_client):
        """Desconexión de Redis"""
        # Primero conectar
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
        
        # Luego desconectar
        redis_conn.disconnect()
        
        assert redis_conn.client is None
        assert redis_conn.is_connected() is False
    
    def test_get_success(self, redis_conn, mock_redis_client):
        """Obtener valor exitosamente"""
        mock_redis_client.get.return_value = b"test_value"
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.get("test_key")
            
            assert result == "test_value"
            mock_redis_client.get.assert_called_once_with("test_key")
    
    def test_get_not_connected(self, redis_conn):
        """Obtener valor cuando no está conectado"""
        result = redis_conn.get("test_key")
        
        assert result is None
    
    def test_get_exception(self, redis_conn, mock_redis_client):
        """Excepción al obtener valor"""
        mock_redis_client.get.side_effect = redis.RedisError("Get failed")
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.get("test_key")
            
            assert result is None
    
    def test_set_success(self, redis_conn, mock_redis_client):
        """Establecer valor exitosamente"""
        mock_redis_client.set.return_value = True
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.set("test_key", "test_value")
            
            assert result is True
            mock_redis_client.set.assert_called_once_with("test_key", "test_value", ex=None)
    
    def test_set_with_expiration(self, redis_conn, mock_redis_client):
        """Establecer valor con expiración"""
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.set("test_key", "test_value", expiration=3600)
            
            assert result is True
            mock_redis_client.set.assert_called_once_with("test_key", "test_value", ex=3600)
    
    def test_set_not_connected(self, redis_conn):
        """Establecer valor cuando no está conectado"""
        result = redis_conn.set("test_key", "test_value")
        
        assert result is False
    
    def test_delete_success(self, redis_conn, mock_redis_client):
        """Eliminar clave exitosamente"""
        mock_redis_client.delete.return_value = 1
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.delete("test_key")
            
            assert result is True
            mock_redis_client.delete.assert_called_once_with("test_key")
    
    def test_delete_key_not_exists(self, redis_conn, mock_redis_client):
        """Eliminar clave que no existe"""
        mock_redis_client.delete.return_value = 0
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.delete("non_existent_key")
            
            assert result is False
    
    def test_exists_true(self, redis_conn, mock_redis_client):
        """Verificar que clave existe"""
        mock_redis_client.exists.return_value = 1
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.exists("test_key")
            
            assert result is True
            mock_redis_client.exists.assert_called_once_with("test_key")
    
    def test_exists_false(self, redis_conn, mock_redis_client):
        """Verificar que clave no existe"""
        mock_redis_client.exists.return_value = 0
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.exists("test_key")
            
            assert result is False
    
    def test_hgetall_success(self, redis_conn, mock_redis_client):
        """Obtener hash completo exitosamente"""
        mock_data = {b"field1": b"value1", b"field2": b"value2"}
        mock_redis_client.hgetall.return_value = mock_data
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.hgetall("test_hash")
            
            expected = {"field1": "value1", "field2": "value2"}
            assert result == expected
            mock_redis_client.hgetall.assert_called_once_with("test_hash")
    
    def test_hgetall_empty(self, redis_conn, mock_redis_client):
        """Obtener hash vacío"""
        mock_redis_client.hgetall.return_value = {}
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.hgetall("empty_hash")
            
            assert result == {}
    
    def test_hset_success(self, redis_conn, mock_redis_client):
        """Establecer campo en hash exitosamente"""
        mock_redis_client.hset.return_value = 1
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.hset("test_hash", "field1", "value1")
            
            assert result is True
            mock_redis_client.hset.assert_called_once_with("test_hash", "field1", "value1")
    
    def test_hset_multiple_fields(self, redis_conn, mock_redis_client):
        """Establecer múltiples campos en hash"""
        data = {"field1": "value1", "field2": "value2"}
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.hset("test_hash", mapping=data)
            
            assert result is True
            mock_redis_client.hset.assert_called_once_with("test_hash", mapping=data)
    
    def test_hdel_success(self, redis_conn, mock_redis_client):
        """Eliminar campo de hash exitosamente"""
        mock_redis_client.hdel.return_value = 1
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.hdel("test_hash", "field1")
            
            assert result is True
            mock_redis_client.hdel.assert_called_once_with("test_hash", "field1")
    
    def test_hdel_field_not_exists(self, redis_conn, mock_redis_client):
        """Eliminar campo que no existe"""
        mock_redis_client.hdel.return_value = 0
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.hdel("test_hash", "non_existent_field")
            
            assert result is False
    
    def test_keys_success(self, redis_conn, mock_redis_client):
        """Obtener claves por patrón exitosamente"""
        mock_keys = [b"key1", b"key2", b"key3"]
        mock_redis_client.keys.return_value = mock_keys
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = redis_conn.keys("pattern*")
            
            expected = ["key1", "key2", "key3"]
            assert result == expected
            mock_redis_client.keys.assert_called_once_with("pattern*")
    
    def test_scan_iter_success(self, redis_conn, mock_redis_client):
        """Iterar claves con scan exitosamente"""
        mock_keys = [b"key1", b"key2", b"key3"]
        mock_redis_client.scan_iter.return_value = iter(mock_keys)
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            result = list(redis_conn.scan_iter("pattern*"))
            
            expected = ["key1", "key2", "key3"]
            assert result == expected
            mock_redis_client.scan_iter.assert_called_once_with(match="pattern*")
    
    def test_connection_context_manager(self, mock_redis_client):
        """Usar RedisConnection como context manager"""
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn = RedisConnection()
            
            with redis_conn as conn:
                assert conn.is_connected() is True
                conn.set("test", "value")
            
            # Verificar que se desconectó automáticamente
            assert redis_conn.is_connected() is False
    
    def test_multiple_operations(self, redis_conn, mock_redis_client):
        """Múltiples operaciones en secuencia"""
        # Configurar mocks
        mock_redis_client.set.return_value = True
        mock_redis_client.get.return_value = b"test_value"
        mock_redis_client.exists.return_value = 1
        mock_redis_client.delete.return_value = 1
        
        with patch('redis.Redis', return_value=mock_redis_client):
            redis_conn.connect()
            
            # Realizar operaciones
            assert redis_conn.set("key1", "value1") is True
            assert redis_conn.get("key1") == "test_value"
            assert redis_conn.exists("key1") is True
            assert redis_conn.delete("key1") is True
            
            # Verificar llamadas
            mock_redis_client.set.assert_called_with("key1", "value1", ex=None)
            mock_redis_client.get.assert_called_with("key1")
            mock_redis_client.exists.assert_called_with("key1")
            mock_redis_client.delete.assert_called_with("key1")
