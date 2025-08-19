# Diagrama de Flujo: Checkout Process

```mermaid
flowchart TD
    A[Usuario envía POST /cart/checkout] --> B{Validar estructura request}
    B -->|Invalid| C[HTTP 422 - Validation Error]
    B -->|Valid| D[Inicializar total_amount = 0<br/>payment_items = []]
    
    D --> E[Para cada item en request.items]
    E --> F[Consultar producto en DB<br/>product_service.get_product_by_id]
    F --> G{¿Producto existe?}
    G -->|No| H[HTTP 404 - Producto no encontrado]
    G -->|Sí| I[Calcular subtotal<br/>total_amount += product.precio * quantity]
    
    I --> J[Agregar item a payment_items]
    J --> K{¿Más items?}
    K -->|Sí| E
    K -->|No| L[Construir payload para API pagos]
    
    L --> M[POST http://localhost:8000/payment/process-payment]
    M --> N{¿Conexión exitosa?}
    N -->|No| O[HTTP 500 - Connection Error]
    N -->|Sí| P{¿response.status_code == 200?}
    
    P -->|No| Q[HTTP response.status_code<br/>Propagar error de API pagos]
    P -->|Sí| R[Construir respuesta exitosa<br/>con transaction_id]
    R --> S[HTTP 200 - Checkout exitoso]
    
    style A fill:#e1f5fe
    style S fill:#c8e6c9
    style C fill:#ffcdd2
    style H fill:#ffcdd2
    style O fill:#ffcdd2
    style Q fill:#ffcdd2
```

# Diagrama de Secuencia: Interacciones del Sistema

```mermaid
sequenceDiagram
    participant U as Usuario
    participant CR as Cart Router
    participant PS as Product Service
    participant DB as Base de Datos
    participant PA as Payment API
    
    U->>CR: POST /cart/checkout {items: [...]}
    
    Note over CR: Validación Pydantic automática
    
    loop Para cada item
        CR->>PS: get_product_by_id(product_id)
        PS->>DB: SELECT * FROM products WHERE id = ?
        DB-->>PS: Product data | null
        PS-->>CR: Product | None
        
        alt Producto no encontrado
            CR-->>U: HTTP 404 - Producto no encontrado
        else Producto encontrado
            Note over CR: Calcular subtotal<br/>Agregar a payment_items
        end
    end
    
    Note over CR: total_amount calculado
    
    CR->>PA: POST /payment/process-payment {items, total_amount}
    
    alt Payment API exitosa
        PA-->>CR: HTTP 200 {transaction_id, status}
        CR-->>U: HTTP 200 {message, total, payment_response}
    else Payment API error
        PA-->>CR: HTTP 4xx/5xx {detail}
        CR-->>U: HTTP 4xx/5xx {error propagado}
    end
```

# Estados del Carrito

```mermaid
stateDiagram-v2
    [*] --> Recibido : POST request
    Recibido --> Validando : Request válido
    Recibido --> Error_Validacion : Request inválido
    
    Validando --> Consultando_Productos
    Consultando_Productos --> Calculando_Total : Todos los productos existen
    Consultando_Productos --> Error_Producto : Producto no encontrado
    
    Calculando_Total --> Procesando_Pago
    Procesando_Pago --> Completado : Pago exitoso
    Procesando_Pago --> Error_Pago : Pago fallido
    Procesando_Pago --> Error_Conexion : Sin conexión
    
    Error_Validacion --> [*] : HTTP 422
    Error_Producto --> [*] : HTTP 404
    Error_Pago --> [*] : HTTP 4xx/5xx
    Error_Conexion --> [*] : HTTP 500
    Completado --> [*] : HTTP 200
```

# Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                     Cart Router                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ CartItem    │  │ CheckoutReq │  │ Response    │         │
│  │ Model       │  │ Model       │  │ Model       │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Product    │    │   Payment    │    │   Database   │
│   Service    │    │     API      │    │   Session    │
│              │    │              │    │              │
│ - get_prod   │    │ - process    │    │ - get_db()   │
│   _by_id()   │    │   _payment   │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Products    │    │   External   │    │  PostgreSQL  │
│  Database    │    │   Payment    │    │  Database    │
│              │    │   Gateway    │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

# Matriz de Responsabilidades

| Componente | Responsabilidad | Input | Output |
|------------|----------------|-------|--------|
| **Cart Router** | Orquestación del checkout | CheckoutRequest | CheckoutResponse / HTTPException |
| **CartItem Model** | Validación de item individual | product_id, quantity | Validated CartItem |
| **CheckoutRequest Model** | Validación de request completo | List[CartItem] | Validated request |
| **Product Service** | Consulta de productos | product_id | Product / None |
| **Payment API** | Procesamiento de pagos | payment_payload | payment_response |
| **Database Session** | Acceso a datos | SQL queries | Database records |

# Patrones de Diseño Aplicados

## 1. Dependency Injection
```python
def checkout(request: CheckoutRequest, db: Session = Depends(get_db)):
    # db session inyectada automáticamente
```

## 2. Repository Pattern
```python
product_service = ProductServiceImpl(db)  # Service wraps repository
product = product_service.get_product_by_id(item.product_id)
```

## 3. DTO (Data Transfer Object)
```python
class CartItem(BaseModel):      # DTO para item individual
class CheckoutRequest(BaseModel): # DTO para request completo
```

## 4. Service Layer
```python
# Business logic encapsulada en el router
total_amount += product.precio * item.quantity
```

## 5. Error Propagation
```python
# Errores se propagan con contexto específico
raise HTTPException(
    status_code=response.status_code,
    detail=response.json().get("detail", "Error genérico")
)
```
