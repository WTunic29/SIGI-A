# Postman (`QA/postman/`)

Colecciones y **entornos** para la API SIGI-A. La app importa todo lo que vive en `QA/postman/` (ver `QA/.postman/resources.yaml`).

## Comando único (`qa check` / `qa smoke`)

Desde `QA/`:

```powershell
.\qa.ps1 check          # validate Postman + xfail budget + pytest
.\qa.ps1 smoke          # Newman health (API levantada; usa pnpm)
.\qa.ps1 install        # pnpm install + recordatorio pip
```

En Linux/macOS: `./qa.sh check` (dar `chmod +x qa.sh` si hace falta).

Dependencias Node: **`pnpm install`** (no npm). Ver `package.json` → `packageManager`.

## Importación rápida

1. **File → Import**
2. Entorno (elige uno; ambos tienen las mismas variables):
   - `environments/SIGI-A-Local.env.yaml`
   - o `environments/SIGI-A.environment.yaml`
3. Colección: `collections/SIGI-A/collection.yaml`  
   Las requests se cargan desde las subcarpetas del mismo árbol (formato Workspace de Postman).

4. Activa el entorno **SIGI-A Local** o **SIGI-A** en el selector superior.

## Estructura

```
postman/
├── collections/SIGI-A/
│   ├── Auth/              # Register, Login, Verify-2FA, Get-Me, Solo-Negocio
│   ├── Health/            # Root, Test-DB
│   ├── Negocios/
│   ├── Productos/
│   ├── Servicios/
│   ├── Empleados/
│   ├── Citas/
│   ├── Pedidos/
│   ├── Pagos/
│   ├── Calificaciones/
│   ├── Notificaciones/
│   ├── Carrito/
│   ├── Favoritos/
│   ├── collection.yaml
│   ├── .resources/
│   └── README.md          # Resumen dentro de la colección
├── newman/               # Smoke JSON ejecutable con Newman (CLI), ver README dentro
├── environments/
│   ├── SIGI-A-Local.env.yaml
│   └── SIGI-A.environment.yaml
└── globals/workspace.globals.yaml
```

Los requests suelen tener **tests** (`afterResponse`) que guardan IDs en variables de entorno tras crear recursos.

## Collection Runner (`order`)

Cada request tiene un **`order`** numérico único en el YAML para que Postman ejecute una pasada ordenada cuando corres **la colección entera**:

- **110–120**: Health  
- **210–250**: Auth (Register → … → Solo-Negocio)  
- **310–350**: Negocios  
- **410–440**: Empleados  
- **510–540**: Servicios  
- **610–640**: Productos  
- **710–750**: Citas  
- **810–830**: Pedidos  
- **910–920**: Pagos  
- **1010–1020**: Calificaciones  
- **1110–1120**: Notificaciones  
- **1200–1210**: Carrito  
- **1300–1310**: Favoritos  

Si solo necesitás un módulo, ejecutá la carpeta correspondiente o arrastrá el orden en Postman; el valor `order` es la convención del repo.

## Variables de entorno

| Variable | Uso |
|----------|-----|
| `base_url` | Origen API (ej. `http://localhost:8000`) |
| `token` | JWT tras **Verify-2FA** |
| `correo_login` | Correo para **Register** y **Login** (deben coincidir) |
| `password_demo` | Contraseña en **Register** y **Login** (misma en ambos) |
| `correo_2fa` | Email devuelto por Login para el paso 2FA |
| `codigo_2fa` | Código de 6 dígitos (**manual**: DB `core.codigo_2fa` o correo en dev) |
| `rol_default` | Rol en Register: `negocio`, `cliente` o `admin` |
| `id_usuario` | Tras Register/Verify-2FA |
| `id_negocio` | Tras **Crear Negocio** o, si está vacío, el primer elemento al **Listar Negocios** (200) |
| `id_empleado` | Tras **Crear Empleado** |
| `id_servicio` | Tras **Crear Servicio** |
| `id_producto` | Tras **Crear Producto** |
| `id_pedido` | Tras **Crear Pedido** |
| `id_pago` | Tras **Registrar Pago** |
| `id_cita` | Tras crear cita OK o valor manual para otros requests de citas |
| `id_notificacion` | Tras **Listar Notificaciones** si hay al menos una (primer elemento) |
| `id_carrito` | Tras **Crear Carrito** o primer ítem en **Listar Carritos** |
| `id_favorito` | Tras **Crear Favorito** |

## Flujo recomendado (manual)

1. **Health**: `GET /`, `GET /test-db`.
2. **Auth**: Register → Login → pegar **`codigo_2fa`** en el entorno → Verify-2FA (rellena `token`). Si `correo_2fa` o `codigo_2fa` faltan, **Verify-2FA** avisa en consola (pre-request).
3. **Negocio** (rol negocio): Crear Negocio → otros recursos usando `{{id_negocio}}`.
4. Empleados / servicios / productos antes de pedidos o citas cuando el orden lo exija.
5. **Citas**: `POST /citas/` puede responder **500** por bug modelo/rutas → `QA/BACKEND_ISSUES_DETECTED.md`.

Consulta **`collections/SIGI-A/README.md`** para tabla de rutas por carpeta.

## Validación estática (`QA/scripts`)

Comprueba que cada `*.request.yaml` tiene `method`, `url`, `order` único y que todas las **`{{variables}}`** existen en **entornos** + **`.resources/definition.yaml`**. También exige mismas claves en `SIGI-A-Local` y `SIGI-A.environment`.

Desde **`QA`**:

```bash
python scripts/validate_postman_workspace.py
```

Se ejecuta también en **`QA (pytest)` en GitHub Actions** antes de pytest.

## Newman (CLI, smoke opcional)

Colección mínima en JSON (**sin auth**) para ejecutar **`GET /`**, **`/test-db`**, **`/openapi.json`** cuando el servidor esté accesible. Instrucciones e integración opcional CI manual: **`newman/README.md`**.

Si `ENVIRONMENT=production` en el backend, `/openapi.json` puede estar **deshabilitado**; en ese caso el tercer request del smoke esperaría fallar a propósito (quitarlo o ejecutar sólo los dos primeros pasos).

## Scripts de mantenimiento (YAML / Postman)

- **`collections/SIGI-A/_convert_crlf.ps1`**: CRLF dentro de esa carpeta.
- **`QA/_fix_all_yaml.ps1`**: todo `QA/postman/**/*.yaml` → UTF-8 sin BOM, LF.
- **`QA/_fix_bom.ps1`**: un subconjunto frecuente (Auth + environments).
- **`QA/_write_postman_files.ps1`**: obsoleto; no regenerar la colección desde ahí (evita pisar requests alineadas con el API).

## Backend en local

Sin backend levantado, las requests fallan por conexión. Desde la raíz del repo (ejemplo):

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

PostgreSQL debe estar configurado en `backend/.env` si usás esa base (Docker u host local).
