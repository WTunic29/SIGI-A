# # README Docker — SIGI-A Backend

## Descripción

SIGI-A Backend utiliza Docker y Docker Compose para ejecutar de manera reproducible y profesional:

* Backend FastAPI
* PostgreSQL
* Variables de entorno
* Networking interno
* Persistencia de datos
* Middleware de seguridad
* Logs automáticos

La dockerización permite levantar todo el entorno sin instalar manualmente Python, PostgreSQL ni dependencias adicionales.

---

# Arquitectura Docker

La solución utiliza dos contenedores principales:

## Backend

Contenedor:

```text
sigia_backend
```

Tecnologías:

* Python
* FastAPI
* SQLAlchemy
* Uvicorn
* JWT
* PostgreSQL Driver

Puerto:

```text
8000
```

---

## PostgreSQL

Contenedor:

```text
sigia_postgres
```

Motor:

```text
PostgreSQL 17
```

Puerto:

```text
5432
```

Persistencia:

```text
postgres_data
```

---

# Archivos Docker Implementados

```text
Dockerfile
Dockerfile.txt
.dockerignore
docker-compose.yml
.env
.env.example
requirements.txt
```

---

# Función de cada archivo

## Dockerfile

Define cómo construir la imagen del backend.

Se encarga de:

* usar Python como base;
* instalar dependencias;
* copiar el proyecto;
* exponer el puerto FastAPI;
* ejecutar Uvicorn.

---

## docker-compose.yml

Permite levantar múltiples servicios simultáneamente.

En SIGI-A:

* Backend FastAPI
* PostgreSQL

También configura:

* networking interno;
* variables de entorno;
* persistencia;
* reinicio automático;
* mapeo de puertos.

---

## .dockerignore

Evita copiar archivos innecesarios o sensibles dentro de la imagen Docker.

Ejemplos:

```text
venv/
.env
logs/
__pycache__/
```

Esto mejora:

* seguridad;
* velocidad de build;
* tamaño de imagen.

---

## .env

Archivo REAL de variables de entorno.

NO debe subirse a GitHub.

Contiene:

* credenciales;
* secretos JWT;
* configuración PostgreSQL;
* configuración producción/desarrollo.

---

## .env.example

Versión pública y segura del `.env`.

Se sube al repositorio para mostrar:

* estructura esperada;
* variables necesarias;
* ejemplo configuración.

---

# Diferencia localhost vs postgres

## Sin Docker

Cuando el backend corre directamente en Windows:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/estetica_app
```

Porque PostgreSQL está instalado localmente.

---

## Con Docker

Cuando el backend corre dentro del contenedor Docker:

```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/estetica_app
```

Importante:

```text
postgres
```

NO es una IP.

Es el nombre del servicio definido en:

```yaml
postgres:
```

Docker crea automáticamente una red interna donde los contenedores se comunican por nombre.

---

# Flujo Docker en SIGI-A

## Paso 1

Docker construye la imagen usando:

```text
Dockerfile
```

---

## Paso 2

Docker Compose levanta:

* FastAPI
* PostgreSQL

---

## Paso 3

FastAPI se conecta automáticamente al contenedor PostgreSQL.

---

## Paso 4

Swagger queda disponible en:

```text
http://localhost:8000/docs
```

---

# Variables de entorno Docker

Ejemplo:

```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/estetica_app
SECRET_KEY=CAMBIAR_EN_PRODUCCION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development
```

---

# Comandos Docker

## Construir imágenes

```bash
docker compose build
```

---

## Construir sin caché

```bash
docker compose build --no-cache
```

---

## Levantar contenedores

```bash
docker compose up
```

---

## Levantar en segundo plano

```bash
docker compose up -d
```

---

## Ver contenedores activos

```bash
docker ps
```

---

## Ver logs

```bash
docker compose logs -f
```

---

## Ver logs backend

```bash
docker compose logs -f backend
```

---

## Ver logs PostgreSQL

```bash
docker compose logs -f postgres
```

---

## Detener contenedores

```bash
docker compose down
```

---

## Eliminar contenedores y volúmenes

```bash
docker compose down -v
```

---

# Logs implementados

SIGI-A implementa middleware automático de logs de seguridad.

Información registrada:

* IP cliente;
* endpoint;
* método HTTP;
* status code;
* user-agent;
* tiempo respuesta.

Archivo:

```text
logs/security.log
```

---

# Security Headers implementados

Middleware implementado:

* X-Content-Type-Options
* X-Frame-Options
* X-XSS-Protection
* Strict-Transport-Security

Objetivo:

* hardening backend;
* mitigación ataques básicos;
* mejores prácticas HTTP.

---

# Swagger y entornos

SIGI-A controla Swagger según entorno.

## Desarrollo

Swagger habilitado:

```text
/docs
```

---

## Producción

Swagger deshabilitado automáticamente usando:

```env
ENVIRONMENT=production
```

---

# Arquitectura enterprise implementada

El backend actualmente incluye:

* FastAPI;
* PostgreSQL;
* SQLAlchemy;
* JWT;
* Refresh Tokens;
* bcrypt;
* 2FA por correo;
* roles y permisos;
* ownership validation;
* sesiones activas;
* logout real;
* invalidación JWT;
* rate limiting;
* logs automáticos;
* security headers;
* Docker;
* docker-compose.

---

# Beneficios obtenidos con Docker

## Reproducibilidad

Cualquier desarrollador puede levantar el backend con:

```bash
docker compose up
```

sin instalar manualmente dependencias.

---

## Portabilidad

El backend puede desplegarse fácilmente en:

* VPS;
* AWS;
* Azure;
* Railway;
* Render;
* DigitalOcean.

---

## Aislamiento

Backend y PostgreSQL quedan separados del sistema operativo.

---

## Consistencia

Todos los ambientes utilizan:

* misma versión Python;
* mismas dependencias;
* misma configuración.

---

# Estado actual

SIGI-A Backend queda preparado para:

* pruebas académicas;
* desarrollo colaborativo;
* despliegue cloud;
* arquitectura enterprise;
* backend profesional.

