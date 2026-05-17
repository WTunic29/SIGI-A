# Colección SIGI-A (Postman Workspace)

YAML alineados con la API FastAPI actual: prefijos `/auth`, `/negocios`, etc. Respuestas **planas** (sin envoltorio `pedido`, `negocio`, …) donde el backend usa `response_model` directamente.

## Carpetas de requests

| Carpeta | Rutas típicas |
|---------|----------------|
| **Auth/** | `/auth/register`, `/auth/login`, `/auth/verify-2fa`, `/auth/me`, `/auth/solo-negocio` |
| **Health/** | `GET /`, `GET /test-db` |
| **Negocios/** | `/negocios/` CRUD |
| **Productos/** | `/productos/` |
| **Servicios/** | `/servicios/` |
| **Empleados/** | `/empleados/` |
| **Citas/** | `/citas/` … (ver problema conocido abajo) |
| **Pedidos/** | `/pedidos` |
| **Pagos/** | `/pagos` |
| **Calificaciones/** | `/calificaciones/` |
| **Notificaciones/** | `/notificaciones/`, `/notificaciones/{{id_notificacion}}/leer` |
| **Carrito/** | `/carritos/` |
| **Favoritos/** | `/favoritos/` |

No hay carpeta **Usuarios/** duplicada: el alta y login están en **Auth/**.

## Contratos y errores conocidos

- **Incidencias documentadas**: `QA/BACKEND_ISSUES_DETECTED.md` (citas Pydantic/SQLAlchemy, duplicados en schemas, etc.).
- **POST /citas/**: el request *Crear Cita* acepta 200/201/500 en tests hasta que el backend unifique modelo y rutas.
- **Orden en Collection Runner**: cada request define `order` (110…1120); ver `QA/postman/README.md`.
- **Lint automático**: `python scripts/validate_postman_workspace.py` (CI + local).
- **Newman smoke (CLI)**: `QA/postman/newman/` (+ `QA/package.json`).


## Orden sugerido para smoke test

1. Health → Root, Test-DB  
2. Auth → Register → Login → (codigo desde DB/email) Verify-2FA → Get-Me  
3. Negocios → crear y guardar `id_negocio`  
4. Empleados → Servicios → Productos según necesites  
5. Pedidos → Pagos, o Citas cuando el backend lo permita  
6. Listar Notificaciones (opcionalmente rellena `id_notificacion` para marcar leída)
