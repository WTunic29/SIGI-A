# Incidencias del backend detectadas por QA

Este archivo se mantiene en `QA/` para que el equipo de backend tenga una lista corta de problemas reproducibles con pytest o Postman, sin depender de cambios en el código del servidor.

## 1. Citas: modelo ORM vs rutas y esquemas Pydantic

**Síntoma:** `POST /citas/` puede responder **500** con `AttributeError: type object 'Cita' has no attribute 'fecha'` (u homólogo en consultas con `hora_inicio` / `hora_fin`).

**Causa probable:** En `app/routes/cita.py` se filtra y se instancia `Cita` con campos `fecha`, `hora_inicio`, `hora_fin`, mientras el modelo SQLAlchemy en `app/models/cita.py` define ventanas temporales con otros nombres (p. ej. `fecha_hora_inicio` / `fecha_hora_fin`). Los esquemas `CitaCreate` / `CitaResponse` en `app/schemas/cita.py` siguen el contrato de fecha/hora separadas.

**QA:** El test `tests/test_routes/test_cita_routes.py::test_cita_creacion_y_actualizacion_estado` está marcado con **`@pytest.mark.xfail`** hasta que el modelo y las rutas coincidan. En Postman, `Crear Cita` acepta temporalmente códigos 200/201/500 y documenta el fallo en la descripción.

**Acción recomendada (backend):** Unificar nombres de columnas en el modelo con lo que usan rutas y migraciones, o adaptar rutas al modelo real y ajustar esquemas/migraciones en bloque.

## 2. Calificaciones: esquema `CalificacionResponse`

**Observación:** En `app/schemas/calificacion.py`, la clase `CalificacionResponse` declara dos veces el campo `id_cliente` (líneas 20–21). Eso puede provocar comportamiento raro en Pydantic o en documentación OpenAPI.

**Acción recomendada (backend):** Dejar una sola definición coherente (`Optional[int]` si aplica, o `int` obligatorio).

## 3. Respuestas JSON “planas” vs envueltas

Varias rutas devuelven el modelo Pydantic directamente (`response_model=FooResponse`), por lo que el JSON **no** incluye claves como `pedido`, `pago`, `cita`, etc. Los requests de Postman en `QA/postman/` fueron alineados a respuestas planas (`id_pedido`, `id_pago`, `id_cita`, …).

---

Última verificación automática (pytest en `QA/`): **54 passed**, **1 xfailed** (cita), salvo cambios posteriores en el repositorio.
