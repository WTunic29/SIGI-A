# Reporte de pruebas pytest — SIGI-A (QA)

**Fecha de ejecución:** 14 de mayo de 2026  
**Ubicación de la suite:** `QA/` (configuración en `QA/pytest.ini`, código bajo prueba en `../backend`)  
**Entorno de esta corrida:** Windows, Python 3.13.3, pytest 9.0.3  

---

## Resumen ejecutivo

| Métrica | Valor |
|--------|--------|
| Tests recopilados | 52 |
| Pasaron | 51 |
| Fallaron | 0 |
| Xfailed (esperado hasta fix backend) | 1 |
| Omitidos | 0 |

**Estado:** la suite en `QA/tests` está en verde salvo **un caso marcado `xfail`**: creación/actualización de **citas** (incoherencia modelo vs rutas en el backend; detalle en `QA/BACKEND_ISSUES_DETECTED.md`).

Las pruebas son de **integración ligera** contra la aplicación FastAPI importada desde `backend/app`, usando una base **SQLite en memoria** y overrides definidos en `QA/tests/conftest.py` (no sustituyen la necesidad de pruebas contra PostgreSQL en entornos reales si aplica).

---

## Cómo reproducir

Desde la raíz del repo o directamente en `QA`:

```powershell
Set-Location "c:\Users\poeta\Documents\SIGI-A\QA"
python -m pytest tests -v
```

Resumen en una línea:

```powershell
python -m pytest tests -q
```

**Requisitos:** el mismo intérprete debe tener instaladas las dependencias del backend (FastAPI, SQLAlchemy, Pydantic, `python-jose`, `httpx`, bcrypt/passlib según el proyecto, pytest, pytest-asyncio, etc.).

---

## Configuración relevante (QA)

- **`QA/pytest.ini`:** `pythonpath = ../backend` para resolver `import app`.
- **`QA/tests/conftest.py`:**
  - Ajuste de `create_engine` para SQLite (sin `connect_args` propios de PostgreSQL).
  - `ATTACH DATABASE ':memory:' AS core` para tablas con esquema `core`.
  - Autofill de PK en SQLite donde hace falta para inserts ORM.
  - Override de `get_current_user` que valida JWT y usuario en BD **sin** exigir fila activa en `sesion` (comportamiento distinto al de producción, solo para tests).
  - Stub de `enviar_codigo_email` para que `/auth/login` no intente SMTP en CI/local.

---

## Resultado por archivo

### `tests/test_models/test_producto_model.py`

| Test | Resultado |
|------|-------------|
| `test_crear_producto_model` | PASSED |
| `test_buscar_producto_model` | PASSED |

### `tests/test_routes/test_negocio_routes.py`

| Test | Resultado |
|------|-------------|
| `TestNegocioRoutes::test_create_negocio_success` | PASSED |
| `TestNegocioRoutes::test_create_negocio_unauthorized_role` | PASSED |
| `TestNegocioRoutes::test_create_negocio_unauthenticated` | PASSED |
| `TestNegocioRoutes::test_get_negocios_public` | PASSED |
| `TestNegocioRoutes::test_get_negocio_by_id_success` | PASSED |
| `TestNegocioRoutes::test_get_negocio_not_found` | PASSED |
| `TestNegocioRoutes::test_update_negocio_success` | PASSED |
| `TestNegocioRoutes::test_update_negocio_unauthorized` | PASSED |
| `TestNegocioRoutes::test_delete_negocio_success` | PASSED |
| `TestNegocioRoutes::test_delete_negocio_unauthorized` | PASSED |
| `TestNegocioRoutes::test_create_negocio_validation_error` | PASSED |

### `tests/test_routes/test_producto_routes.py`

| Test | Resultado |
|------|-------------|
| `TestProductoRoutes::test_create_producto_success` | PASSED |
| `TestProductoRoutes::test_create_producto_unauthorized` | PASSED |
| `TestProductoRoutes::test_create_producto_unauthenticated` | PASSED |
| `TestProductoRoutes::test_get_productos_by_negocio` | PASSED |
| `TestProductoRoutes::test_get_productos_sin_negocio` | PASSED |

### `tests/test_routes/test_user_routes.py`

| Test | Resultado |
|------|-------------|
| `TestUserRoutes::test_register_user_success` | PASSED |
| `TestUserRoutes::test_register_duplicate_email` | PASSED |
| `TestUserRoutes::test_register_invalid_email` | PASSED |
| `TestUserRoutes::test_register_missing_required_fields` | PASSED |
| `TestUserRoutes::test_login_success` | PASSED |
| `TestUserRoutes::test_login_invalid_credentials` | PASSED |
| `TestUserRoutes::test_login_invalid_email_format` | PASSED |
| `TestUserRoutes::test_get_me_success` | PASSED |
| `TestUserRoutes::test_get_me_unauthorized` | PASSED |
| `TestUserRoutes::test_get_me_invalid_token` | PASSED |
| `TestUserRoutes::test_register_different_roles` | PASSED |
| `TestUserRoutes::test_register_invalid_role` | PASSED |

### `tests/test_schemas/test_producto_schema.py`

| Test | Resultado |
|------|-------------|
| `test_producto_schema_valido` | PASSED |
| `test_producto_schema_invalido` | PASSED |

### `tests/test_schemas_standalone.py`

| Test | Resultado |
|------|-------------|
| `TestUserSchemas::test_usuario_create_valid` | PASSED |
| `TestUserSchemas::test_usuario_create_invalid_email` | PASSED |
| `TestNegocioSchemas::test_negocio_create_valid` | PASSED |
| `TestProductoSchemas::test_producto_create_valid` | PASSED |

### Otros módulos de rutas / humo (misma corrida)

| Archivo | Tests | Resultado |
|---------|-------|-------------|
| `tests/test_routes/test_carrito_routes.py` | 1 | PASSED |
| `tests/test_routes/test_health_routes.py` | 2 | PASSED |
| `tests/test_routes/test_notificacion_routes.py` | 2 | PASSED |
| `tests/test_routes/test_openapi_smoke.py` | 1 | PASSED |
| `tests/test_routes/test_pedido_pago_routes.py` | 4 | PASSED |
| `tests/test_routes/test_servicio_empleado_routes.py` | 4 | PASSED |
| `tests/test_routes/test_cita_routes.py` | 1 | **XFAIL** (bug backend citas; ver `BACKEND_ISSUES_DETECTED.md`) |

---

## Advertencias (warnings) observadas

No impiden que las pruebas pasen; conviene planificar limpieza en el backend cuando haya margen:

1. **Pydantic v2:** varios `schema.py` del backend usan `class Config` en modelos de respuesta; Pydantic avisa migración a `ConfigDict`.
2. **SQLAlchemy / datetime:** uso de `datetime.utcnow()` en defaults o rutas (deprecación en favor de datetimes con zona).
3. **Plugins:** `pytest-asyncio` en modo auto (sin tests async en esta lista).

---

## Notas de alineación con la API real

- **Login:** el backend responde con flujo **2FA** (`requieres_2fa`, etc.); los tests no envían correo real gracias al stub.
- **Mensajes de error:** p. ej. credenciales incorrectas usan el texto **`Credenciales inválidas`** en la API.
- **Productos:** creación vía `POST /productos/` devuelve **200** con el `response_model` actual (no 201), alineado con los tests.
- **Listado de negocios:** `GET /negocios/` exige JWT en la API; los tests usan usuario con rol **cliente** para listar.
- **Pedidos y pagos:** las respuestas son JSON **planos** (`PedidoResponse`, `PagoResponse`), no objetos anidados bajo `pedido` / `pago`.
- **Citas:** `PUT /citas/{id}` con cuerpo `CitaUpdate` (no existe `PUT .../estado`). El fallo actual es de persistencia/consulta ORM frente al modelo real.

---

## Próximos pasos sugeridos (opcional)

- Corregir en backend lo documentado en `QA/BACKEND_ISSUES_DETECTED.md` y quitar el `xfail` del test de citas cuando aplique.
- Ejecutar la misma suite en CI (carpeta `QA`).
- Añadir cobertura (`pytest-cov`) con umbral mínimo si el equipo lo define.

---

*Documento actualizado para reflejar la suite en `QA/tests` y la configuración descrita. Vuelve a generar o pegar la salida de `python -m pytest tests -v` tras cambios importantes en pruebas o entorno.*
