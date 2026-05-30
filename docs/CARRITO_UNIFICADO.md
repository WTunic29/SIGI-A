# Carrito unificado SIGI-A — Productos + citas → pago → factura

Documentación del flujo implementado en **backend**, **frontend** y **QA** (mayo 2026). Reemplaza la compra y el agendamiento directos por un **carrito único** con **checkout atómico** y **comprobante imprimible**.

---

## Resumen ejecutivo

| Antes | Ahora |
|-------|--------|
| Producto → pedido inmediato (`POST /pedidos/`) | Producto → **agregar al carrito** |
| Cita → `POST /citas/` al confirmar | Servicio agendado → **agregar al carrito** (cita se crea al pagar) |
| Pago manual por pedido en “Mis pedidos” | **Un checkout** desde el carrito |
| Sin factura | **Factura** (`core.facturas`) + pantalla imprimible |
| APIs de carrito sin uso en el front | Front integrado con `/carritos/activo/me` y checkout |

---

## Arquitectura por capas

```mermaid
flowchart TB
    subgraph cliente["Cliente (navegador)"]
        UI[index.html + main.js]
        CART[Sección Carrito]
        FAC[Sección Factura + print]
    end

    subgraph api["Backend FastAPI"]
        R_CAR[routes/carrito.py]
        R_DET[routes/carrito_detalle.py]
        R_FAC[routes/factura.py]
        SVC[services/checkout.py]
        HEL[utils/carrito_helpers.py]
        R_CIT[routes/cita.py - disponibilidad]
    end

    subgraph db["PostgreSQL schema core"]
        T_CAR[(carritos)]
        T_CD[(carrito_detalle)]
        T_PED[(pedidos)]
        T_PD[(pedido_detalle)]
        T_CIT[(citas)]
        T_PAG[(pagos)]
        T_FAC[(facturas)]
    end

    UI --> CART
    CART -->|JWT Bearer| R_CAR
    CART --> R_DET
    CART -->|checkout| SVC
    FAC --> R_FAC
    R_DET --> HEL
    R_DET --> R_CIT
    SVC --> T_PED
    SVC --> T_CIT
    SVC --> T_PAG
    SVC --> T_FAC
    R_CAR --> T_CAR
    R_DET --> T_CD
```

### Responsabilidades

| Capa | Responsabilidad |
|------|-----------------|
| **Frontend** | UX: agregar ítems, listar carrito, modal de pago, vista e impresión de factura |
| **carrito_helpers** | Validar ítems, normalizar precios, enriquecer respuestas con nombres |
| **checkout.py** | Transacción: pedido(s) + citas + pago + factura + cierre de carrito |
| **cita.py** | Reutiliza `validar_disponibilidad_cita` al agregar servicio y al pagar |
| **PostgreSQL** | Persistencia; migración `c3d4e5f6a7b8` en AWS/Linux vía Alembic |

---

## Flujo de usuario (frontend)

```mermaid
flowchart LR
    A[Explorar negocios] --> B{¿Qué agrega?}
    B -->|Producto| C[Tienda → Agregar al carrito]
    B -->|Servicio| D[Detalle negocio → Horario → Agregar al carrito]
    C --> E[Mi Carrito]
    D --> E
    E --> F[Revisar total]
    F --> G[Pagar e imprimir factura]
    G --> H[POST checkout]
    H --> I[Pantalla Factura]
    I --> J[window.print]
```

### Pantallas y acciones

| Pantalla | ID HTML | Acciones principales |
|----------|---------|----------------------|
| Tienda | `#tienda-usuario` | Agregar producto (cantidad) |
| Agendar | `#detalle-negocio` | Agregar servicio con fecha/hora/empleado |
| Carrito | `#carrito-usuario` | Listar, quitar ítem, pagar |
| Factura | `#factura-usuario` | Ver comprobante, imprimir |
| Mis pedidos | `#mis-pedidos-usuario` | Ver factura de pedidos ya pagados |

### Configuración API (Linux / AWS)

El front detecta la URL del backend sin rutas fijas de Windows:

```javascript
// frontend/js/main.js — prioridad:
// 1) window.SIGIA_API_BASE (definir en index.html)
// 2) localhost → :8000
// 3) mismo host puerto 10000 (típico AWS)
// 4) mismo origin si hay reverse proxy
```

En producción, antes de `main.js`:

```html
<script>window.SIGIA_API_BASE = "https://api.tu-dominio.com";</script>
```

---

## Flujo de checkout (backend)

```mermaid
sequenceDiagram
    participant U as Cliente
    participant API as POST /carritos/{id}/checkout
    participant CH as checkout.py
    participant DB as PostgreSQL

    U->>API: metodo_pago, referencia_externa
    API->>CH: ejecutar_checkout()
    CH->>DB: Validar carrito activo + ítems
    loop Por cada id_negocio
        CH->>DB: Crear pedido (total calculado)
        loop Por cada ítem
            alt producto
                CH->>DB: Descontar stock
                CH->>DB: pedido_detalle (producto)
            else servicio
                CH->>CH: validar_disponibilidad_cita
                CH->>DB: Crear cita confirmada + detalle_cita
                CH->>DB: pedido_detalle (servicio, id_cita)
            end
        end
        CH->>DB: pedido.estado = pagado
        CH->>DB: Crear pago aprobado
        CH->>DB: Crear factura FAC-AAAA-NNNNNN
    end
    CH->>DB: carrito.estado = cerrado
    CH-->>U: pedidos, pagos, facturas, resumen
```

### Reglas de negocio en checkout

| Regla | Comportamiento |
|-------|----------------|
| Carrito vacío | Error 400 |
| Carrito no activo | Error 400 |
| Multi-negocio | Un **pedido + pago + factura** por cada `id_negocio` |
| Total | Calculado en servidor (`precio_unitario × cantidad`) |
| Producto | Valida stock; descuenta al confirmar pago |
| Servicio | Valida horario; crea **cita** solo al pagar (estado `confirmada`) |
| Transacción | Rollback si falla cualquier paso |
| Factura | Numeración `FAC-{año}-{secuencia 6 dígitos}` |

---

## Modelo de datos

### Tablas involucradas

```mermaid
erDiagram
    carritos ||--o{ carrito_detalle : contiene
    carritos }o--|| usuarios : pertenece
    carrito_detalle }o--o| productos : producto
    carrito_detalle }o--o| servicios : servicio
    pedidos ||--o{ pedido_detalle : tiene
    pedidos ||--o| pagos : paga
    pedidos ||--o| facturas : factura
    pedido_detalle }o--o| citas : cita_servicio
    citas ||--o{ detalle_cita : detalle
```

### `core.carrito_detalle` (campos nuevos)

| Campo | Tipo | Uso |
|-------|------|-----|
| `id_negocio` | bigint | Agrupar checkout por negocio |
| `id_empleado` | bigint | Servicio agendado |
| `fecha_cita` | date | Día de la cita |
| `hora_inicio` | time | Inicio del bloque |
| `hora_fin` | time | Fin (calculado o enviado) |
| `observaciones` | text | Notas opcionales |
| `tipo_item` | varchar | `producto` \| `servicio` |
| `id_producto` / `id_servicio` | bigint | Referencia al catálogo |
| `cantidad` | int | Productos: N; servicios: 1 |
| `precio_unitario` | numeric | Precio en servidor al agregar |

### `core.facturas` (tabla nueva)

| Campo | Descripción |
|-------|-------------|
| `id_factura` | PK |
| `id_pedido` | Pedido pagado |
| `id_pago` | Pago asociado |
| `numero_factura` | Único, ej. `FAC-2026-000001` |
| `subtotal` / `total` | Montos |
| `estado` | `emitida` por defecto |
| `fecha_emision` | Timestamp |

### `core.pedido_detalle` (campo nuevo)

| Campo | Descripción |
|-------|-------------|
| `id_cita` | FK lógica a cita creada en checkout (solo ítems `servicio`) |

---

## API REST

### Carrito y detalle

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/carritos/activo/me` | cliente | Carrito activo + detalles + total (crea si no existe) |
| POST | `/carritos/` | cliente | Crear carrito manual |
| GET | `/carritos/{id}` | cliente, admin | Obtener carrito |
| POST | `/carrito-detalle/` | cliente, admin | Agregar ítem (validado) |
| GET | `/carrito-detalle/` | cliente, admin | Listar detalles del usuario |
| PUT | `/carrito-detalle/{id}` | cliente, admin | Actualizar cantidad |
| DELETE | `/carrito-detalle/{id}` | cliente, admin | Quitar ítem |

### Checkout y factura

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/carritos/{id}/checkout` | cliente | Pago + pedido(s) + citas + factura(s) |
| GET | `/facturas/{id_factura}` | cliente, negocio, admin | Detalle para imprimir |
| GET | `/facturas/pedido/{id_pedido}` | cliente, negocio, admin | Factura por pedido |

### Ejemplo: agregar producto

```http
POST /carrito-detalle/
Authorization: Bearer {token}
Content-Type: application/json

{
  "id_carrito": 1,
  "tipo_item": "producto",
  "id_negocio": 3,
  "id_producto": 12,
  "cantidad": 2,
  "precio_unitario": 25000
}
```

El servidor **sobrescribe** `precio_unitario` con el precio actual del producto y valida stock.

### Ejemplo: agregar servicio (cita pendiente de pago)

```http
POST /carrito-detalle/
Authorization: Bearer {token}

{
  "id_carrito": 1,
  "tipo_item": "servicio",
  "id_negocio": 3,
  "id_servicio": 5,
  "id_empleado": 2,
  "fecha_cita": "2026-06-15",
  "hora_inicio": "10:00:00",
  "cantidad": 1,
  "precio_unitario": 45000,
  "observaciones": "Primera visita"
}
```

Valida disponibilidad con la misma lógica que `GET /citas/disponibilidad`.

### Ejemplo: checkout

```http
POST /carritos/1/checkout
Authorization: Bearer {token}

{
  "metodo_pago": "efectivo",
  "referencia_externa": "CHK-20260529-001"
}
```

Respuesta (resumen):

```json
{
  "message": "Checkout completado",
  "id_carrito": 1,
  "pedidos": [{ "id_pedido": 10, "estado": "pagado", "total": "50000.00" }],
  "pagos": [{ "id_pago": 8, "estado_pago": "aprobado" }],
  "facturas": [{ "numero_factura": "FAC-2026-000001", "lineas": [...] }],
  "resumen": [{ "id_pedido": 10, "id_factura": 3, "numero_factura": "FAC-2026-000001" }]
}
```

---

## Archivos creados o modificados

### Backend

| Archivo | Cambio |
|---------|--------|
| `app/models/carrito_detalle.py` | Campos de agendamiento + negocio |
| `app/models/pedido_detalle.py` | `id_cita` |
| `app/models/factura.py` | **Nuevo** modelo |
| `app/schemas/carrito_detalle.py` | Validación `tipo_item` + campos cita |
| `app/schemas/carrito_completo.py` | **Nuevo** respuesta carrito activo |
| `app/schemas/checkout.py` | **Nuevo** request/response checkout |
| `app/schemas/factura.py` | **Nuevo** factura con líneas |
| `app/services/checkout.py` | **Nuevo** orquestación atómica |
| `app/utils/carrito_helpers.py` | **Nuevo** validación y enriquecimiento |
| `app/routes/carrito.py` | `/activo/me`, `/checkout` |
| `app/routes/carrito_detalle.py` | Validación al crear |
| `app/routes/factura.py` | **Nuevo** rutas factura |
| `app/main.py` | Registro router `factura` |
| `alembic/versions/c3d4e5f6a7b8_*.py` | **Nueva** migración PostgreSQL |
| `scripts/apply_checkout_migration.sh` | Script bash para AWS/Linux |

### Frontend

| Archivo | Cambio |
|---------|--------|
| `frontend/js/main.js` | Carrito, checkout, factura, `API_BASE` dinámico |
| `frontend/index.html` | Secciones `#carrito-usuario`, `#factura-usuario`, menú Carrito |
| `frontend/css/styles.css` | Estilos carrito, factura, `@media print` |

### QA

| Archivo | Cambio |
|---------|--------|
| `QA/tests/test_routes/test_carrito_checkout_routes.py` | **Nuevo** tests checkout + factura |
| `QA/tests/contract/openapi_prefixes.py` | Prefijo `/facturas` |
| `QA/tests/conftest.py` | Override `get_db` en `factura` |
| `QA/BACKEND_ISSUES_DETECTED.md` | Conteo tests actualizado |

---

## Despliegue en Linux / AWS

```bash
# 1. Dependencias
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Variables (.env)
# DATABASE_URL=postgresql://user:pass@host:5432/sigia

# 3. Migración (obligatoria antes de usar carrito/checkout)
chmod +x scripts/apply_checkout_migration.sh
./scripts/apply_checkout_migration.sh

# 4. Servidor
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

### Checklist post-despliegue

| Paso | Verificación |
|------|----------------|
| Migración Alembic `head` | Tabla `core.facturas` y columnas nuevas en `carrito_detalle` |
| `GET /carritos/activo/me` con JWT cliente | 200 + carrito vacío o con ítems |
| Front con `SIGIA_API_BASE` | Peticiones al host correcto |
| Checkout de prueba | Pedido `pagado`, factura `FAC-…`, carrito `cerrado` |

---

## Pruebas automatizadas

```bash
cd QA
python -m pip install -r ../backend/requirements.txt -r requirements-ci.txt
python -m pytest tests/test_routes/test_carrito_checkout_routes.py -v
```

| Test | Qué valida |
|------|------------|
| `test_carrito_activo_me` | Creación/obtención carrito + agregar producto + total |
| `test_checkout_producto_genera_factura` | Checkout, pedido pagado, factura `FAC-*` |

Estado global documentado en `QA/BACKEND_ISSUES_DETECTED.md`: **56 passed**, **1 xfailed** (bug previo en `POST /citas/` directo, independiente del carrito).

---

## Comparación: flujo antiguo vs unificado

```mermaid
flowchart TB
    subgraph viejo["Flujo anterior"]
        V1[Producto] --> V2[POST pedido]
        V3[Cita] --> V4[POST citas]
        V2 --> V5[Pagar pedido suelto]
        V4 --> V6[Sin pago integrado]
    end

    subgraph nuevo["Flujo unificado"]
        N1[Producto o servicio] --> N2[POST carrito-detalle]
        N2 --> N3[GET activo/me]
        N3 --> N4[POST checkout]
        N4 --> N5[Factura + print]
    end
```

---

## Limitaciones y trabajo futuro

| Tema | Estado actual |
|------|----------------|
| Pasarela PayU real | Solo registro de pago (`metodo_pago: payu`); sin redirección |
| `POST /citas/` directo | Sigue existiendo; bug ORM documentado en QA (xfail) |
| Factura fiscal DIAN | Comprobante interno, no facturación electrónica legal |
| Carrito cerrado | Tras checkout hay que usar nuevo carrito activo (se crea automáticamente) |
| Citas en carrito de otro usuario | No aplicable; carrito ligado a `id_usuario` JWT |

---

## Referencias rápidas

| Necesito… | Ubicación |
|-----------|-----------|
| Lógica de checkout | `backend/app/services/checkout.py` |
| Validar ítem al agregar | `backend/app/utils/carrito_helpers.py` |
| UI carrito / pago | `frontend/js/main.js` (sección CARRITO Y CHECKOUT) |
| Migración DB | `backend/alembic/versions/c3d4e5f6a7b8_carrito_checkout_factura.py` |
| Tests | `QA/tests/test_routes/test_carrito_checkout_routes.py` |
| Swagger local | `http://127.0.0.1:8000/docs` |

---

*Última actualización: 29/05/2026 — SIGI-A / SIGI-E*
