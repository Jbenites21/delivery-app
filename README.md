# Delivery App API

Una API REST para aplicación de delivery construida con FastAPI y Redis.

## 🚀 Características

- ✅ Autenticación de usuarios con Redis
- ✅ Registro y login de usuarios
- ✅ Gestión de sesiones con tokens
- ✅ Almacenamiento en Redis
- ✅ Containerización con Docker
- ✅ Documentación automática con Swagger

## 📋 Requisitos

- Python 3.10+
- Redis Server
- Docker (opcional)

## 🛠️ Instalación

### Opción 1: Instalación Local

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Edita el archivo .env con tu configuración
   ```

3. **Iniciar Redis:**
   ```bash
   # En Windows con Docker
   docker run -d -p 6379:6379 redis:latest
   
   # O instalar Redis localmente
   ```

4. **Ejecutar la aplicación:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Opción 2: Con Docker Compose

1. **Ejecutar todo el stack:**
   ```bash
   docker-compose up -d
   ```

## 📚 Endpoints de la API

### Autenticación

- **POST** `/registrar` - Registrar nuevo usuario
- **POST** `/login` - Iniciar sesión
- **POST** `/logout` - Cerrar sesión

### Perfil

- **GET** `/profile/{token}` - Obtener información del usuario

### Utilidades

- **GET** `/` - Estado de la API
- **GET** `/health` - Health check
- **GET** `/redis/stats` - Estadísticas de Redis

### Documentación

- **GET** `/docs` - Documentación Swagger UI
- **GET** `/redoc` - Documentación ReDoc

## 🧪 Pruebas

1. **Ejecutar pruebas automáticas:**
   ```bash
   python test_redis.py
   ```

2. **Pruebas manuales con curl:**

   **Registrar usuario:**
   ```bash
   curl -X POST "http://localhost:8000/registrar" \
        -H "Content-Type: application/json" \
        -d '{"nombre":"Juan Pérez","email":"juan@ejemplo.com","password":"mipassword123"}'
   ```

   **Iniciar sesión:**
   ```bash
   curl -X POST "http://localhost:8000/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"juan@ejemplo.com","password":"mipassword123"}'
   ```

## 🏗️ Estructura del Proyecto

```
delivery-app/
├── main.py                 # Aplicación principal FastAPI
├── models/
│   └── usermodels.py      # Modelos Pydantic
├── database/
│   ├── __init__.py
│   └── redis_connection.py # Conexión y operaciones Redis
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuración de la app
├── test_redis.py          # Script de pruebas
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Imagen Docker
├── docker-compose.yml    # Orquestación de servicios
├── .env.example         # Ejemplo de variables de entorno
└── README.md           # Este archivo
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Aplicación  
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=True

# Seguridad
SECRET_KEY=your-secret-key-here
TOKEN_EXPIRE_HOURS=24
```

## 💾 Redis - Estructura de Datos

### Usuarios
```
Key: user:{email}
Value: {
  "nombre": "string",
  "email": "string", 
  "password_hash": "string",
  "created_at": "timestamp"
}
```

### Sesiones
```
Key: session:{token}
Value: {
  "email": "string",
  "nombre": "string",
  "created_at": "timestamp"
}
TTL: 24 horas
```

## 🔐 Seguridad

- Contraseñas hasheadas con SHA-256 (⚠️ usar bcrypt en producción)
- Tokens de sesión únicos generados con `secrets`
- Sesiones con expiración automática en Redis
- Validación de datos con Pydantic

## 🚧 Próximas Funcionalidades

- [ ] Productos y categorías
- [ ] Carrito de compras
- [ ] Gestión de pedidos
- [ ] Restaurantes y delivery
- [ ] Autenticación con JWT
- [ ] Base de datos MongoDB
- [ ] Tests unitarios
- [ ] CI/CD

## 🐛 Troubleshooting

**Error de conexión Redis:**
```bash
# Verificar que Redis esté ejecutándose
docker ps | grep redis

# Ver logs de Redis
docker logs <redis-container-id>
```

**Error en la API:**
```bash
# Ver logs de la aplicación
docker-compose logs app
```

## 📝 Licencia

Este proyecto es de uso educativo.