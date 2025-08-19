# Especificación API: Cart Router

## Información General

- **Base URL:** `http://localhost:8000`
- **Prefijo:** `/cart`
- **Versión:** v1.0
- **Formato:** JSON
- **Autenticación:** No requerida (por ahora)

---

## Endpoints

### POST /cart/checkout

Procesa el checkout de un carrito de compras.

#### Request

**URL:** `POST /cart/checkout`

**Headers:**
```http
Content-Type: application/json
Accept: application/json
```

**Body Schema:**
```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "product_id": {
            "type": "string",
            "description": "UUID del producto"
          },
          "quantity": {
            "type": "integer",
            "minimum": 1,
            "description": "Cantidad solicitada"
          }
        },
        "required": ["product_id", "quantity"]
      },
      "description": "Lista de items en el carrito"
    }
  },
  "required": ["items"]
}
```

**Example Request:**
```json
{
  "items": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440000",
      "quantity": 2
    },
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440001",
      "quantity": 1
    }
  ]
}
```

#### Responses

##### 200 OK - Checkout Exitoso

**Headers:**
```http
Content-Type: application/json
```

**Body Schema:**
```json
{
  "type": "object",
  "properties": {
    "message": {
      "type": "string",
      "example": "Compra procesada exitosamente."
    },
    "total": {
      "type": "number",
      "format": "float",
      "description": "Total calculado de la compra"
    },
    "payment_response": {
      "type": "object",
      "properties": {
        "message": {
          "type": "string"
        },
        "status": {
          "type": "string",
          "enum": ["completed", "pending", "failed"]
        },
        "transaction_id": {
          "type": "string",
          "pattern": "^txn_[a-zA-Z0-9]+$"
        }
      }
    }
  }
}
```

**Example Response:**
```json
{
  "message": "Compra procesada exitosamente.",
  "total": 45.75,
  "payment_response": {
    "message": "Pago simulado exitosamente.",
    "status": "completed",
    "transaction_id": "txn_abc123xyz789"
  }
}
```

##### 404 Not Found - Producto No Encontrado

**Headers:**
```http
Content-Type: application/json
```

**Body Schema:**
```json
{
  "type": "object",
  "properties": {
    "detail": {
      "type": "string",
      "pattern": "^Producto con ID .+ no encontrado\\.$"
    }
  }
}
```

**Example Response:**
```json
{
  "detail": "Producto con ID 550e8400-e29b-41d4-a716-446655440000 no encontrado."
}
```

##### 422 Unprocessable Entity - Datos Inválidos

**Headers:**
```http
Content-Type: application/json
```

**Body Schema:**
```json
{
  "type": "object",
  "properties": {
    "detail": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {"type": "string"},
          "loc": {"type": "array"},
          "msg": {"type": "string"},
          "input": {}
        }
      }
    }
  }
}
```

**Example Response:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "items", 0, "quantity"],
      "msg": "Field required",
      "input": {
        "product_id": "550e8400-e29b-41d4-a716-446655440000"
      }
    }
  ]
}
```

##### 400/500 - Errores de Payment API

Los errores de la API de pagos se propagan con el mismo código de estado.

**Example Response (400):**
```json
{
  "detail": "El monto total debe ser mayor a cero."
}
```

**Example Response (500):**
```json
{
  "detail": "Error en el procesamiento del pago."
}
```

---

## Validaciones

### Nivel Request (FastAPI/Pydantic)

1. **items** debe ser una lista (puede estar vacía)
2. **product_id** es requerido, tipo string
3. **quantity** es requerido, tipo entero
4. **quantity** debe ser convertible a int (acepta strings numéricos)

### Nivel Business Logic

1. **Existencia de producto:** Cada product_id debe existir en la base de datos
2. **Disponibilidad:** Los productos deben estar marcados como disponibles
3. **Cálculo de total:** Debe ser preciso con decimales

### Nivel Payment API

1. **Monto válido:** total_amount > 0 (validado por Payment API)
2. **Estructura de items:** Debe coincidir con el formato esperado

---

## Dependencias Externas

### Product Service
- **Método:** `get_product_by_id(product_id: str)`
- **Retorna:** `Product | None`
- **Error:** No lanza excepciones, retorna None si no encuentra

### Payment API
- **URL:** `http://localhost:8000/payment/process-payment`
- **Método:** POST
- **Timeout:** No configurado (default requests)
- **Retry:** No implementado

### Database
- **Sesión:** Inyectada via `Depends(get_db)`
- **Transacciones:** Solo lectura
- **Pool:** Manejado por SQLAlchemy

---

## Comportamientos Especiales

### Carrito Vacío
```json
{
  "items": []
}
```
- **Comportamiento:** total_amount = 0
- **Payment API:** Recibe monto cero
- **Resultado:** Depende de validación de Payment API

### Items Duplicados
```json
{
  "items": [
    {"product_id": "abc", "quantity": 2},
    {"product_id": "abc", "quantity": 3}
  ]
}
```
- **Comportamiento:** Se procesan independientemente
- **Total:** (precio * 2) + (precio * 3)
- **Recomendación:** Cliente debe agregar cantidades

### Precisión Decimal
```json
{
  "items": [
    {"product_id": "abc", "quantity": 3}
  ]
}
```
Con precio = 1.99:
- **Cálculo:** 1.99 * 3 = 5.97
- **Precisión:** Mantenida en float
- **Payment API:** Recibe 5.97

---

## Códigos de Error HTTP

| Código | Significado | Origen | Acción |
|--------|-------------|---------|---------|
| 200 | Checkout exitoso | Cart Router | Procesar respuesta |
| 400 | Error de Payment API | Payment API | Mostrar error al usuario |
| 404 | Producto no encontrado | Cart Router | Revisar product_id |
| 422 | Datos inválidos | FastAPI | Corregir request |
| 500 | Error interno/conexión | Cart Router/Payment API | Reintentar más tarde |

---

## Rate Limiting

**Estado Actual:** No implementado

**Recomendación:**
- 10 requests por minuto por IP
- 100 requests por hora por usuario autenticado
- Burst allowance: 3 requests en 5 segundos

---

## Caching

**Estado Actual:** No implementado

**Oportunidades:**
- Cache de productos consultados (TTL: 5 minutos)
- Cache de respuestas de Payment API exitosas
- Cache de validaciones de producto

---

## Monitoreo y Logging

### Métricas Recomendadas

```json
{
  "endpoint": "/cart/checkout",
  "method": "POST",
  "status_code": 200,
  "response_time_ms": 150,
  "items_count": 3,
  "total_amount": 45.75,
  "payment_api_time_ms": 80,
  "db_queries": 3,
  "transaction_id": "txn_abc123"
}
```

### Logs de Error

```json
{
  "timestamp": "2025-08-18T10:30:00Z",
  "level": "ERROR",
  "endpoint": "/cart/checkout",
  "error_type": "product_not_found",
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "request_id": "req_xyz789"
}
```

---

## Testing

### Casos de Prueba Funcionales

1. ✅ **Checkout exitoso item único**
2. ✅ **Checkout exitoso múltiples items**
3. ✅ **Producto no encontrado**
4. ✅ **Error de Payment API**
5. ✅ **Datos de entrada inválidos**
6. ✅ **Carrito vacío**
7. ✅ **Cálculos con decimales**

### Casos de Prueba No Funcionales

- **Performance:** < 200ms response time (95th percentile)
- **Carga:** 100 requests/second sin degradación
- **Disponibilidad:** 99.9% uptime
- **Recuperación:** < 30 segundos tras fallo de Payment API

---

## Versioning

### Estrategia de Versionado

**Actual:** Sin versioning explícito

**Propuesta:**
- URL Path: `/v1/cart/checkout`
- Header: `API-Version: 1.0`
- Query param: `?version=1.0`

### Cambios Breaking

Considerados breaking changes:
- Modificar esquema de request/response
- Cambiar códigos de estado HTTP
- Remover campos de respuesta
- Cambiar validaciones existentes

### Cambios Non-Breaking

No breaking:
- Agregar campos opcionales a response
- Agregar nuevas validaciones más permisivas
- Mejorar mensajes de error
- Optimizaciones de performance

---

## Seguridad

### Validación de Input

✅ **Implementado:**
- Validación de tipos Pydantic
- Sanitización automática de JSON

❌ **Pendiente:**
- Validación de format UUID para product_id
- Límites en quantity (max value)
- Validación de tamaño de array items

### Prevención de Ataques

❌ **No Implementado:**
- Rate limiting
- Input size limits
- SQL injection prevention (delegado a ORM)
- XSS prevention (API only)

### Datos Sensibles

- ❌ No se maneja información de pago directamente
- ❌ No se almacenan datos de tarjetas
- ❌ Logs no contienen información sensible

---

## Performance

### Métricas Actuales

- **Response time:** ~150ms promedio
- **DB queries:** N+1 (una por producto)
- **Payment API call:** ~80ms
- **Memory usage:** Mínimo (stateless)

### Optimizaciones Propuestas

1. **Batch product queries:** Una sola query para todos los productos
2. **Async payment calls:** Non-blocking payment processing
3. **Connection pooling:** Reutilizar conexiones HTTP
4. **Product caching:** Cache local de productos frecuentes

### SLA Propuesto

- **Availability:** 99.9%
- **Response time:** < 200ms (95th percentile)
- **Error rate:** < 0.1%
- **Throughput:** > 100 RPS
