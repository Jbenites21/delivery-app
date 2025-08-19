# Caso de Uso: Carrito de Compras (Cart)

## Información General

**Módulo:** Cart Router  
**Archivo:** `infraestructure/api/routers/cart.py`  
**Descripción:** Gestión del carrito de compras y procesamiento de checkout  
**Actor Principal:** Cliente/Usuario  
**Casos de Uso Relacionados:** Payment Processing, Product Management  

## Resumen Ejecutivo

El módulo de carrito de compras permite a los usuarios seleccionar productos, calcular totales y procesar pagos de manera segura y eficiente. Integra la validación de productos disponibles con el sistema de pagos para proporcionar una experiencia de compra completa.

---

## Caso de Uso Principal: Checkout de Carrito

### UC-CART-001: Procesar Checkout

**Objetivo:** Procesar la compra de los items seleccionados en el carrito del usuario

**Actor Principal:** Cliente  
**Actores Secundarios:** Sistema de Pagos, Sistema de Inventario  
**Tipo:** Primario, Esencial  
**Complejidad:** Media  

### Precondiciones
- El usuario ha seleccionado al menos un producto
- Los productos están disponibles en el sistema
- El sistema de pagos está operativo
- La base de datos de productos está accesible

### Postcondiciones
- **Éxito:** 
  - La compra ha sido procesada exitosamente
  - Se ha generado un ID de transacción
  - El total ha sido calculado correctamente
  - Se retorna confirmación del pago
  
- **Fallo:**
  - Se informa el error específico al usuario
  - No se procesa ningún cargo
  - El estado del carrito permanece inalterado

---

## Flujo Principal de Eventos

### Escenario Exitoso

1. **[Usuario]** Envía solicitud de checkout con lista de items
   ```http
   POST /cart/checkout
   Content-Type: application/json
   
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

2. **[Sistema]** Valida la estructura del request
   - Verifica que `items` sea una lista válida
   - Valida que cada item tenga `product_id` y `quantity`
   - Confirma que `quantity` sea un número positivo

3. **[Sistema]** Inicializa variables de procesamiento
   ```python
   total_amount = 0
   payment_items = []
   ```

4. **[Sistema]** Para cada item en el carrito:
   
   a. **Consulta producto en base de datos**
   ```python
   product = product_service.get_product_by_id(item.product_id)
   ```
   
   b. **Valida existencia del producto**
   - Si el producto no existe → Ir a **Flujo Alternativo FA-1**
   
   c. **Calcula subtotal**
   ```python
   total_amount += product.precio * item.quantity
   ```
   
   d. **Prepara item para pago**
   ```python
   payment_items.append({
       "product_id": item.product_id, 
       "quantity": item.quantity
   })
   ```

5. **[Sistema]** Construye payload para API de pagos
   ```python
   payment_payload = {
       "items": payment_items,
       "total_amount": total_amount
   }
   ```

6. **[Sistema]** Invoca API de pagos
   ```python
   response = requests.post(
       "http://localhost:8000/payment/process-payment",
       json=payment_payload
   )
   ```

7. **[Sistema de Pagos]** Procesa el pago
   - Valida el monto total
   - Simula procesamiento de pago
   - Genera ID de transacción único

8. **[Sistema]** Evalúa respuesta de pagos
   - Si `response.status_code == 200` → Continúa al paso 9
   - Si `response.status_code != 200` → Ir a **Flujo Alternativo FA-2**

9. **[Sistema]** Construye respuesta exitosa
   ```json
   {
     "message": "Compra procesada exitosamente.",
     "total": 45.75,
     "payment_response": {
       "message": "Pago simulado exitosamente.",
       "status": "completed",
       "transaction_id": "txn_abc123xyz"
     }
   }
   ```

10. **[Sistema]** Retorna respuesta HTTP 200 al usuario

---

## Flujos Alternativos

### FA-1: Producto No Encontrado

**Trigger:** El producto especificado no existe en la base de datos

**Flujo:**
1. **[Sistema]** Detecta que `product_service.get_product_by_id()` retorna `None`
2. **[Sistema]** Lanza excepción HTTP 404
   ```python
   raise HTTPException(
       status_code=status.HTTP_404_NOT_FOUND,
       detail=f"Producto con ID {item.product_id} no encontrado."
   )
   ```
3. **[Usuario]** Recibe respuesta de error
   ```json
   {
     "detail": "Producto con ID 550e8400-e29b-41d4-a716-446655440000 no encontrado."
   }
   ```

**Postcondición:** El proceso se detiene, no se procesa ningún pago

### FA-2: Error en API de Pagos

**Trigger:** La API de pagos retorna un código de error

**Flujo:**
1. **[Sistema]** Recibe respuesta de error de la API de pagos
2. **[Sistema]** Extrae el mensaje de error de la respuesta
   ```python
   error_detail = response.json().get("detail", "Error en el procesamiento del pago.")
   ```
3. **[Sistema]** Lanza excepción HTTP con el mismo código de estado
   ```python
   raise HTTPException(
       status_code=response.status_code,
       detail=error_detail
   )
   ```
4. **[Usuario]** Recibe el error propagado desde la API de pagos

**Postcondición:** El error se propaga al usuario con contexto específico

### FA-3: Error de Conectividad

**Trigger:** Falla la conexión con la API de pagos

**Flujo:**
1. **[Sistema]** `requests.post()` lanza `RequestException`
2. **[Sistema]** La excepción se propaga al nivel superior
3. **[Usuario]** Recibe error HTTP 500 (manejado por FastAPI)

**Postcondición:** El sistema informa error de conectividad

### FA-4: Datos de Entrada Inválidos

**Trigger:** El request no cumple con el esquema Pydantic

**Flujo:**
1. **[FastAPI]** Valida automáticamente el request contra `CheckoutRequest`
2. **[FastAPI]** Detecta campos faltantes o tipos incorrectos
3. **[FastAPI]** Retorna HTTP 422 con detalles de validación
   ```json
   {
     "detail": [
       {
         "type": "missing",
         "loc": ["body", "items", 0, "quantity"],
         "msg": "Field required",
         "input": {"product_id": "abc123"}
       }
     ]
   }
   ```

**Postcondición:** El request es rechazado antes de procesar

---

## Casos Extremos

### CE-1: Carrito Vacío

**Escenario:** Usuario envía lista de items vacía

**Comportamiento:**
- `total_amount = 0`
- `payment_items = []`
- La API de pagos recibe monto cero
- Depende de la lógica de la API de pagos si acepta o rechaza

**Consideración:** Podría requerir validación adicional

### CE-2: Cantidad Muy Grande

**Escenario:** Usuario solicita cantidad excesiva de un producto

**Comportamiento Actual:**
- El sistema calcula el total sin validar stock
- No hay límites en las cantidades

**Recomendación:** Implementar validación de inventario

### CE-3: Precio Cero

**Escenario:** Producto con precio 0 en base de datos

**Comportamiento:**
- El cálculo incluye `0 * quantity = 0`
- El total puede ser cero o muy bajo
- La API de pagos determina si acepta

### CE-4: Productos Duplicados

**Escenario:** El mismo product_id aparece múltiples veces

**Comportamiento Actual:**
- Cada aparición se procesa independientemente
- Las cantidades no se suman automáticamente
- Puede resultar en cálculos inesperados

**Recomendación:** Implementar agregación de items duplicados

---

## Modelos de Datos

### CartItem
```python
class CartItem(BaseModel):
    product_id: str      # UUID del producto
    quantity: int        # Cantidad solicitada (> 0)
```

**Validaciones:**
- `product_id`: Requerido, formato string
- `quantity`: Requerido, entero positivo (validado por Pydantic)

### CheckoutRequest
```python
class CheckoutRequest(BaseModel):
    items: List[CartItem]  # Lista de items del carrito
```

**Validaciones:**
- `items`: Lista requerida (puede estar vacía)
- Cada elemento debe ser un `CartItem` válido

### Respuesta de Éxito
```json
{
  "message": "Compra procesada exitosamente.",
  "total": 45.75,
  "payment_response": {
    "message": "Pago simulado exitosamente.",
    "status": "completed", 
    "transaction_id": "txn_abc123xyz"
  }
}
```

---

## Integraciones

### Sistema de Productos
- **Servicio:** `ProductServiceImpl`
- **Método:** `get_product_by_id(product_id: str)`
- **Propósito:** Validar existencia y obtener precio del producto
- **Dependencia:** Base de datos de productos

### Sistema de Pagos
- **Endpoint:** `POST http://localhost:8000/payment/process-payment`
- **Payload:**
  ```json
  {
    "items": [{"product_id": "...", "quantity": 1}],
    "total_amount": 45.75
  }
  ```
- **Respuesta Exitosa:**
  ```json
  {
    "message": "Pago simulado exitosamente.",
    "status": "completed",
    "transaction_id": "txn_..."
  }
  ```

### Base de Datos
- **Dependencia:** `get_db()` - Sesión de SQLAlchemy
- **Uso:** Inyección de dependencia para acceso a productos
- **Transacciones:** Solo lectura (consultas de productos)

---

## Consideraciones de Seguridad

### Validación de Entrada
- ✅ **Tipos de datos:** Validación automática Pydantic
- ✅ **Campos requeridos:** Enforced por el modelo
- ❌ **Límites de cantidad:** No implementado
- ❌ **Validación de UUID:** Product_id como string libre

### Manejo de Errores
- ✅ **Propagación controlada:** Errores de pago se propagan con contexto
- ✅ **Información específica:** Mensajes de error descriptivos
- ❌ **Rate limiting:** No implementado
- ❌ **Logging de seguridad:** No implementado

### Integridad de Datos
- ✅ **Cálculos precisos:** Uso de float para precios
- ✅ **Estado consistente:** No modifica datos en caso de error
- ❌ **Validación de inventario:** No verifica stock disponible
- ❌ **Transacciones distribuidas:** No garantiza consistencia entre sistemas

---

## Métricas y Monitoreo

### Métricas Recomendadas
- **Tiempo de respuesta:** Latencia del endpoint checkout
- **Tasa de éxito:** Porcentaje de checkouts exitosos
- **Errores de producto:** Frecuencia de productos no encontrados
- **Errores de pago:** Tipos y frecuencia de errores de la API de pagos
- **Tamaño de carrito:** Distribución de cantidad de items por checkout

### Logging Sugerido
```python
# Inicio de checkout
logger.info(f"Checkout initiated", extra={
    "items_count": len(request.items),
    "user_id": user_id  # Si hay autenticación
})

# Producto no encontrado
logger.warning(f"Product not found", extra={
    "product_id": item.product_id,
    "checkout_id": checkout_id
})

# Checkout exitoso
logger.info(f"Checkout completed", extra={
    "total_amount": total_amount,
    "transaction_id": transaction_id,
    "processing_time": processing_time
})
```

---

## Casos de Prueba

### Casos Positivos
1. **Checkout con item único** → HTTP 200
2. **Checkout con múltiples items** → HTTP 200  
3. **Checkout con carrito vacío** → HTTP 200 (según API de pagos)
4. **Cálculo con decimales** → Precisión correcta

### Casos Negativos  
1. **Producto inexistente** → HTTP 404
2. **API de pagos no disponible** → HTTP 500
3. **Datos de entrada inválidos** → HTTP 422
4. **Quantity negativa o cero** → HTTP 422

### Casos Límite
1. **Cantidad muy alta** → Comportamiento actual
2. **Producto con precio cero** → Cálculo correcto
3. **Items duplicados** → Procesamiento independiente
4. **Request malformado** → HTTP 422

---

## Roadmap y Mejoras

### Mejoras Inmediatas (Sprint Actual)
- [ ] Agregar cart router a `main.py` 
- [ ] Implementar `get_product_by_id` en ProductService
- [ ] Validación de quantity > 0
- [ ] Logging básico de operaciones

### Mejoras a Corto Plazo (1-2 Sprints)
- [ ] Validación de inventario disponible
- [ ] Agregación automática de items duplicados  
- [ ] Rate limiting para prevenir abuso
- [ ] Timeout configuration para API calls
- [ ] Circuit breaker para API de pagos

### Mejoras a Mediano Plazo (3-6 Sprints)
- [ ] Persistencia de carrito en sesión/DB
- [ ] Gestión de carritos abandonados
- [ ] Descuentos y promociones
- [ ] Cálculo de impuestos
- [ ] Múltiples métodos de pago
- [ ] Notificaciones de confirmación

### Mejoras a Largo Plazo (6+ Sprints)
- [ ] Checkout asíncrono con cola de mensajes
- [ ] Integración con sistemas de inventario en tiempo real
- [ ] Análisis de carritos abandonados
- [ ] Recomendaciones de productos
- [ ] Sistema de puntos/loyalty
- [ ] Integración con logistics/shipping

---

## Conclusión

El módulo de carrito de compras implementa los flujos esenciales para el procesamiento de órdenes de manera efectiva. Proporciona validación de productos, cálculo preciso de totales e integración con sistemas de pago.

**Fortalezas:**
- Arquitectura clara y separación de responsabilidades
- Manejo robusto de errores
- Integración bien definida con sistemas externos
- Validación automática de datos de entrada

**Áreas de Mejora:**
- Validación de inventario disponible
- Manejo de items duplicados
- Configuración de timeouts y circuit breakers
- Logging y monitoreo más completos

El sistema está preparado para evolucionar hacia un carrito más sofisticado con persistencia, gestión de sesiones y capacidades avanzadas de e-commerce.
