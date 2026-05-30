# QA — SIGI-A

Carpeta de **calidad y pruebas** del proyecto [SIGI-A](https://github.com) (Sistema de Gestión Inteligente de Estética). Aquí vive todo lo necesario para validar la API del backend **sin modificar** `backend/`, `frontend/` ni `database/` desde esta documentación: los tests **importan** el código de `../backend/app` vía `pytest.ini`.

---

## Qué incluye QA

| Capa | Herramienta | Para qué sirve |
|------|-------------|----------------|
| **Automatizado (CI/local)** | **pytest** | Contrato de rutas, auth simulada, SQLite en memoria |
| **Manual / exploratorio** | **Postman** (YAML workspace) | Flujo completo con 2FA, CRUD por módulos |
| **Smoke HTTP (CLI)** | **Newman** + **pnpm** | `/`, `/test-db`, `/openapi.json` y auth parcial sin Postman Desktop |
| **Validación estática** | Scripts Python | YAML Postman coherente, presupuesto de `xfail` |
| **CI** | GitHub Actions | pytest + cobertura en cada PR; Newman opcional contra URL pública |

Documentación complementaria:

- [`GUIA_TESTS.md`](GUIA_TESTS.md) — pasos detallados de pytest y solución de problemas
- [`postman/README.md`](postman/README.md) — Postman y Newman en profundidad
- [`BACKEND_ISSUES_DETECTED.md`](BACKEND_ISSUES_DETECTED.md) — bugs conocidos reproducibles desde QA

---

## Estructura de la carpeta

```
QA/
├── qa.ps1 / qa.sh              # Entrada única: check | smoke | install
├── pytest.ini                  # pythonpath → ../backend, marcadores smoke/contract
├── requirements-ci.txt         # pytest, httpx, pytest-cov, PyYAML (pip)
├── package.json                # Newman (pnpm); ver packageManager
├── pnpm-lock.yaml              # Lockfile Node (usar pnpm, no npm)
├── .gitignore                  # node_modules, reports, caches pytest
│
├── scripts/
│   ├── validate_postman_workspace.py   # Lint YAML + variables {{…}}
│   └── check_xfail_budget.py           # Máx. 1 @pytest.mark.xfail documentado
│
├── tests/
│   ├── conftest.py             # SQLite memoria, JWT por defecto, overrides get_db
│   ├── contract/
│   │   └── openapi_prefixes.py # Prefijos exigidos en /openapi.json
│   ├── test_models/
│   ├── test_schemas/
│   └── test_routes/            # health, auth, negocios, citas (xfail), etc.
│
├── postman/
│   ├── collections/SIGI-A/     # *.request.yaml (Postman Desktop / Local View)
│   ├── environments/           # SIGI-A-Local.env.yaml, SIGI-A.environment.yaml
│   ├── newman/                 # smoke.collection.json, auth-partial, README
│   └── README.md
│
├── .postman/
│   └── resources.yaml          # Registra todo bajo postman/ en Postman IDE
│
├── BACKEND_ISSUES_DETECTED.md
├── GUIA_TESTS.md
└── README.md                   # Este archivo
```

Colección Postman por carpetas: **Auth**, **Health**, **Negocios**, **Empleados**, **Servicios**, **Productos**, **Citas**, **Pedidos**, **Pagos**, **Calificaciones**, **Notificaciones**, **Carrito**, **Favoritos**.

---

## Requisitos

| Herramienta | Uso |
|-------------|-----|
| **Python 3.12+** (3.13 en local OK) | pytest |
| **pip** | `backend/requirements.txt` + `QA/requirements-ci.txt` |
| **Node 18+** + **pnpm 9** | Newman (`pnpm-lock.yaml`). Si no hay `pnpm` en PATH, `qa.ps1` usa `npx pnpm@9.15.9` |
| **Postman** (opcional) | Pruebas manuales con YAML del repo |
| **API levantada** (opcional) | Newman smoke y Postman contra `base_url`; pytest **no** necesita PostgreSQL |

---

## Inicio rápido (recomendado)

### 1. Instalar dependencias Python

Desde la **raíz del repositorio** o desde `QA/`:

```powershell
pip install -r backend\requirements.txt -r QA\requirements-ci.txt
```

```bash
pip install -r backend/requirements.txt -r QA/requirements-ci.txt
```

### 2. Ejecutar la suite completa de QA

```powershell
cd QA
.\qa.ps1 check
```

```bash
cd QA
chmod +x qa.sh    # solo la primera vez en Unix
./qa.sh check
```

**`check` hace, en orden:**

1. `python scripts/validate_postman_workspace.py` — YAML válido, `order` únicos, variables `{{…}}` declaradas  
2. `python scripts/check_xfail_budget.py` — como máximo **1** test con `@pytest.mark.xfail` (citas)  
3. `python -m pytest tests -q --tb=line` — suite pytest (~54 passed, 1 xfailed)

No hace falta `backend/.env` para JWT: `tests/conftest.py` rellena `SECRET_KEY`, `ALGORITHM`, etc., si están vacías.

### 3. (Opcional) Node + Newman

```powershell
cd QA
.\qa.ps1 install    # pnpm install (o npx pnpm@9.15.9)
# Levantar API en otro terminal, luego:
.\qa.ps1 smoke
```

Equivalente manual:

```bash
cd QA
pnpm install
pnpm run postman:newman:smoke
# Auth parcial (register + login, sin Verify-2FA):
pnpm run postman:newman:auth-partial
```

Cambiar URL:

```bash
pnpm run postman:newman:smoke -- --env-var base_url=http://127.0.0.1:9000
```

---

## Comandos `qa.ps1` / `qa.sh`

| Comando | Descripción |
|---------|-------------|
| **`check`** | Validadores + pytest (uso diario y mismo espíritu que CI) |
| **`install`** | `pnpm install` + mensaje recordatorio de `pip install` |
| **`smoke`** | Newman colección health/OpenAPI (requiere API en `base_url`) |

Argumentos extra se pasan a pytest, por ejemplo:

```powershell
.\qa.ps1 check -- tests/test_routes/test_user_routes.py -v
```

---

## Tests automatizados (pytest)

### Cómo funciona

- `pytest.ini` añade `../backend` al `PYTHONPATH` e importa `app` como en producción.
- `conftest.py` fuerza `DATABASE_URL=sqlite:///:memory:`, parchea engines SQLite y sustituye auth por JWT + usuario en BD (sin tabla `sesion` real).
- Rutas con `get_db` local (`carrito`, `favorito`, `pedido`, etc.) se redirigen al mismo override.

### Ejecutar manualmente

```powershell
cd QA
python -m pytest tests -v --tb=short
```

Solo contrato OpenAPI:

```powershell
python -m pytest tests/test_routes/test_openapi_smoke.py -v
```

Marcador `contract` (definido en `pytest.ini`):

```powershell
python -m pytest -m contract -v
```

Cobertura HTML (informe en `QA/htmlcov/`):

```powershell
python -m pytest tests --cov=app --cov-report=html
```

### Módulos cubiertos (rutas)

| Archivo de test | Área |
|-----------------|------|
| `test_health_routes.py` | `/`, `/test-db` |
| `test_user_routes.py` | `/auth/*` |
| `test_negocio_routes.py` | `/negocios/` |
| `test_producto_routes.py` | `/productos/` |
| `test_servicio_empleado_routes.py` | servicios, empleados |
| `test_pedido_pago_routes.py` | pedidos, pagos |
| `test_notificacion_routes.py` | notificaciones |
| `test_calificacion_routes.py` | calificaciones |
| `test_favorito_routes.py` | `/favoritos/` |
| `test_inventario_routes.py` | `/inventario-movimientos/` |
| `test_carrito_routes.py` | `/carritos/` |
| `test_cita_routes.py` | citas (**xfail** — ver incidencias) |
| `test_openapi_smoke.py` | prefijos en `/openapi.json` |
| `test_models/`, `test_schemas/` | modelos y Pydantic aislados |

Prefijos OpenAPI canónicos: [`tests/contract/openapi_prefixes.py`](tests/contract/openapi_prefixes.py).

### Estado esperado

- **~54 passed**, **1 xfailed** (creación/estado de cita hasta alinear backend).
- Si aparece un **segundo** `xfail`, `check_xfail_budget.py` falla hasta documentarlo en `BACKEND_ISSUES_DETECTED.md`.

---

## Postman (pruebas manuales)

### Importar en Postman Desktop

1. [Descargar Postman](https://www.postman.com/downloads/)
2. **Import** → `QA/postman/environments/SIGI-A-Local.env.yaml` (o `SIGI-A.environment.yaml`)
3. **Import** → `QA/postman/collections/SIGI-A/collection.yaml`  
   (las requests se cargan desde las subcarpetas; ver `QA/.postman/resources.yaml` si usas Local View)

Activar entorno **SIGI-A Local** y revisar `base_url` (por defecto `http://localhost:8000`).

### Flujo recomendado

1. **Health** → Root, Test-DB  
2. **Auth** → Register → Login → pegar **`codigo_2fa`** en el entorno → Verify-2FA (guarda `token`)  
3. **Negocio** (rol `negocio` en `rol_default`) → Crear Negocio → empleados / servicios / productos  
4. Pedidos, pagos, calificaciones, notificaciones, carrito, favoritos según necesidad  
5. **Citas**: `POST /citas/` puede devolver **500** (bug documentado)

Register y Login usan **`{{correo_login}}`** y **`{{password_demo}}`** del entorno (misma contraseña en ambos).

Obtener código 2FA en desarrollo (PostgreSQL):

```sql
SELECT codigo FROM core.codigo_2fa
WHERE id_usuario = <id_usuario>
ORDER BY id_codigo DESC LIMIT 1;
```

### Collection Runner y `order`

Cada `*.request.yaml` tiene un campo **`order`** único (110…1310) para ejecutar **toda la colección** en orden lógico. Detalle por rangos en [`postman/README.md`](postman/README.md).

### Variables de entorno (resumen)

| Variable | Uso |
|----------|-----|
| `base_url` | URL del API |
| `token` | JWT tras Verify-2FA |
| `correo_login`, `password_demo` | Register + Login |
| `correo_2fa`, `codigo_2fa` | Verify-2FA |
| `rol_default` | `cliente`, `negocio` o `admin` en Register |
| `id_usuario`, `id_negocio`, `id_empleado`, … | Rellenados por scripts `afterResponse` |

Lista completa: [`postman/README.md`](postman/README.md).

### Validar YAML sin abrir Postman

```powershell
cd QA
python scripts/validate_postman_workspace.py
```

(Incluido en `qa check` y en CI.)

---

## Newman (smoke por terminal)

Newman **no** ejecuta los YAML del workspace; usa JSON en `postman/newman/`:

| Colección | Contenido |
|-----------|-----------|
| `smoke.collection.json` | `GET /`, `/test-db`, `/openapi.json` |
| `auth-partial.collection.json` | Register + Login (sin 2FA) |

Entorno: `smoke.postman_environment.json` (`base_url`, `correo_login`, `password_demo`, `rol_default`).

Guía: [`postman/newman/README.md`](postman/newman/README.md).

**Producción:** si `ENVIRONMENT=production`, `/openapi.json` puede estar desactivado; el request OpenAPI del smoke puede fallar por diseño.

---

## CI (GitHub Actions)

### QA (pytest) — automático

Archivo: [`.github/workflows/qa-pytest.yml`](../.github/workflows/qa-pytest.yml)

Se dispara en push/PR a `main`, `master` o `develop` cuando cambian `QA/**` o `backend/**`.

Pasos: instalar pip → `validate_postman_workspace` → `check_xfail_budget` → pytest con **cobertura** y **JUnit** → artefacto `qa-pytest-reports` (`reports/junit.xml`, `reports/coverage.xml`).

### QA (Newman smoke) — manual

Archivo: [`.github/workflows/qa-newman-smoke.yml`](../.github/workflows/qa-newman-smoke.yml)

**workflow_dispatch** con:

- `base_url` — API accesible desde GitHub (no sirve `localhost` de tu PC)
- `collection` — `smoke` o `auth-partial`

Usa **pnpm** con `pnpm-lock.yaml`.

---

## Scripts de mantenimiento

| Script | Función |
|--------|---------|
| [`scripts/validate_postman_workspace.py`](scripts/validate_postman_workspace.py) | Coherencia YAML Postman |
| [`scripts/check_xfail_budget.py`](scripts/check_xfail_budget.py) | Límite de tests xfail |
| [`_fix_all_yaml.ps1`](_fix_all_yaml.ps1) | UTF-8 sin BOM + LF en `postman/**/*.yaml` |
| [`_fix_bom.ps1`](_fix_bom.ps1) | Subconjunto Auth + environments |
| [`_write_postman_files.ps1`](_write_postman_files.ps1) | **Obsoleto** — no regenerar colección desde aquí |

---

## Incidencias conocidas del backend

Todo lo reproducible desde QA (pytest/Postman) está en [`BACKEND_ISSUES_DETECTED.md`](BACKEND_ISSUES_DETECTED.md).

Resumen:

1. **Citas** — modelo ORM vs rutas (`fecha` / `hora_*` vs `fecha_hora_*`) → pytest **xfail**, Postman acepta 500 en Crear Cita.  
2. **Calificaciones** — posible duplicado de `id_cliente` en schema.  
3. Respuestas JSON **planas** (`id_negocio`, no `{ "negocio": … }`) — Postman alineado a eso.

---

## Preparar el backend para pruebas manuales / Newman

pytest **no** necesita el servidor corriendo. Postman y Newman **sí**:

```powershell
cd backend
# Configurar backend\.env (PostgreSQL, SMTP, JWT) según backend/README.md o READMEDOCKER.md
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger (si no es producción): `http://127.0.0.1:8000/docs`

---

## Referencias rápidas

| Necesito… | Ir a… |
|-----------|--------|
| Pasos largos de pytest | [`GUIA_TESTS.md`](GUIA_TESTS.md) |
| Variables Postman y orden Runner | [`postman/README.md`](postman/README.md) |
| Newman CLI | [`postman/newman/README.md`](postman/newman/README.md) |
| Bugs API documentados | [`BACKEND_ISSUES_DETECTED.md`](BACKEND_ISSUES_DETECTED.md) |
| Código del API | `../backend/` |
| Un solo comando local | `.\qa.ps1 check` |

---

## Notas

- **Roles:** muchos endpoints exigen `cliente`, `negocio` o `admin` en el JWT.  
- **2FA:** flujo completo solo en Postman o integrando código desde DB/correo.  
- **pnpm vs npm:** usar `pnpm install`; `package-lock.json` no se versiona (ver `QA/.gitignore`).  
- **Artefactos locales:** `reports/`, `htmlcov/`, `.pytest_cache/`, `node_modules/` están ignorados por git.
