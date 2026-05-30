# Newman (CLI) — smoke contra la API

La colección en YAML dentro de `collections/SIGI-A/` es para **Postman Desktop** (workspace). Newman **solo** ejecuta JSON en formato colección Postman v2.1.

Este directorio tiene una **`smoke.collection.json`** mínima (sin JWT) para chequear rápido si el servidor responde.

## Cuándo usarla

- Después de levantar el backend (`uvicorn` o Docker): comprobar `/`, `/test-db`, `/openapi.json`.
- Para flujos con **auth/2FA** seguir usando Postman Desktop o **`pytest`** en `QA/tests` (más automatizable que Newman con tu stack actual).

## Requisitos

- Node.js 18+ (recomendado).
- O bien `npx newman` sin instalar proyecto (ver abajo).

## Opción A — desde `QA/` con pnpm (recomendado)

```bash
cd QA
pnpm install
pnpm run postman:newman:smoke
```

Auth parcial (register + login, sin Verify-2FA):

```bash
pnpm run postman:newman:auth-partial
```

Sobreescribir URL:

```bash
pnpm run postman:newman:smoke -- --env-var base_url=http://127.0.0.1:9000
```

O usar el script: `.\qa.ps1 smoke` (Windows) / `./qa.sh smoke` (Unix).

## Opción B — pnpm dlx (sin instalar en el proyecto)

```bash
cd QA
pnpm dlx newman@6 run postman/newman/smoke.collection.json -e postman/newman/smoke.postman_environment.json
```

En **Windows/PowerShell** las rutas son equivalentes usando `QA\`.

## Producción (`ENVIRONMENT=production`)

El backend suele exponer **`/openapi.json`** y **`/docs` desactivados** (ver `backend/app/main.py`). En ese modo el último caso del smoke (**OpenAPI**) puede fallar si es intencional: omite ese request en Newman o ejecuta solo los dos primeros.

## Workflow manual en GitHub Actions

Hay un workflow opcional **`QA (Newman smoke)`** con `workflow_dispatch` e input `base_url` apuntando a un entorno público/accesible desde `ubuntu-latest`.
