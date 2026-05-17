# SIGI-A - Sistema Inteligente de Gestión para Centros de Estética

Sistema inteligente de gestión para centros de estética (barberías, peluquerías, tatuajes, centros de belleza, etc.).

---

## 🎯 **Visión General**

SIGI-A es una **plataforma SaaS integral** diseñada para digitalizar y optimizar la gestión de negocios del sector de estética y belleza. Conecta barberías, peluquerías, salones de tatuajes y centros de belleza en un ecosistema unificado.

## 🏗️ **Arquitectura Técnica**

### **Backend (FastAPI + PostgreSQL)**
- **API RESTful** con autenticación JWT + 2FA
- **Base de datos relacional** con schema optimizado
- **Roles de usuario**: cliente, negocio, admin
- **Modelos SQLAlchemy** con relaciones entre entidades
- **Schemas Pydantic** para validación automática
- **Endpoints FastAPI** con seguridad por rol

### **Frontend (Web)**
- **Interfaz responsiva** HTML/CSS/JavaScript
- **Dashboard diferenciado** por rol
- **Gestión visual** de citas y servicios
- **Experiencia móvil-friendly**

### **QA & Testing**
- **Postman** (workspace YAML) para flujos manuales y Runner
- **pytest** en `QA/tests` (SQLite en memoria, sin PostgreSQL)
- **Newman** (pnpm) para smoke HTTP y auth parcial
- **GitHub Actions**: pytest en PR; Newman opcional contra URL pública
- Detalle en [`QA/README.md`](QA/README.md)

---

## Descripción

SIGI-A es una plataforma que permite conectar múltiples negocios de estética en un solo sistema. Los usuarios pueden:

- Ver negocios cercanos
- Agendar citas
- Calificar servicios
- Comprar servicios/productos

Los negocios pueden:

- Gestionar empleados
- Administrar citas en tiempo real
- Controlar inventario
- Ver reportes y métricas

---

## 📁 **Estructura del Proyecto**

```
SIGI-A/
│
├── backend/                 # API FastAPI + PostgreSQL
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── core/
│   │   ├── utils/
│   │   ├── middleware/
│   │   ├── database.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── QA/                      # Calidad: pytest, Postman, Newman, CI
│   ├── tests/               # Suite pytest (pythonpath → ../backend)
│   ├── pytest.ini
│   ├── scripts/             # validate_postman_workspace, check_xfail_budget
│   ├── postman/             # Colecciones YAML + newman/
│   ├── qa.ps1 / qa.sh       # check | smoke | install
│   └── README.md
│
├── frontend/                # Interfaz web (HTML/CSS/JS)
│   ├── CSS/
│   ├── JS/
│   ├── SIGI-E/
│   └── index.html
│
├── database/
│   ├── schema_actual.sql
│   └── seeds_actual.sql
│
├── .github/workflows/       # qa-pytest.yml, qa-newman-smoke.yml
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv
```

### 2. Activar entorno virtual

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` basado en `.env.example` y completar los valores. Para el backend en desarrollo, ver también `backend/.env.example` si existe.

### 5. Ejecutar el backend

```bash
cd backend
uvicorn app.main:app --reload
```

El backend estará disponible en `http://127.0.0.1:8000`.

---

## Frontend

Abrir `frontend/index.html` en el navegador o servir la carpeta `frontend/` desde un servidor web simple.

---

## QA / Postman

Importar la colección desde `QA/postman/collections/` y el entorno desde `QA/postman/environments/`.

Para la suite automatizada (validadores + pytest):

```powershell
cd QA
pip install -r ..\backend\requirements.txt -r requirements-ci.txt
.\qa.ps1 check
```

Documentación completa: [`QA/README.md`](QA/README.md).

---

## **Características Principales**

### **Para Usuarios Finales**
- **Descubrimiento**: Encuentra negocios cercanos
- **Agendamiento**: Reserva citas online
- **Calificaciones**: Valora servicios recibidos
- **Comercio**: Compra productos y servicios

### **Para Negocios**
- **Gestión de Empleados**: Controla tu equipo
- **Dashboard en Tiempo Real**: Monitorea operaciones
- **Control de Inventario**: Gestiona stock y productos
- **Reportes y Métricas**: Analiza rendimiento del negocio

## 🛠️ **Stack Tecnológico**

### **Backend**
- **Framework**: Python 3.12+, FastAPI
- **ORM**: SQLAlchemy 2.0
- **Base de Datos**: PostgreSQL 16 con schema `core`
- **Validación**: Pydantic v2
- **Testing**: pytest + pytest-cov en `QA/`

### **Frontend**
- **Markup**: HTML5
- **Estilos**: CSS3 + Responsive Design
- **JavaScript**: Vanilla JS
- **UI**: Dashboard diferenciado por rol

### **Seguridad**
- **Autenticación**: JWT con access/refresh tokens
- **2FA**: Verificación por email
- **Password Hashing**: bcrypt
- **Rate Limiting**: slowapi
- **Roles**: cliente, negocio, admin

### **DevOps**
- **Contenerización**: Docker + Docker Compose
- **CI**: GitHub Actions (`qa-pytest`, Newman smoke manual)
- **Testing QA**: Postman + Newman
- **Documentación**: Swagger/OpenAPI
- **Logging**: Middleware personalizado

## 📊 **Estado Actual del Proyecto**

| Componente | Estado | Notas |
|------------|--------|--------|
| Backend API | Funcional | Ver Swagger en `/docs` |
| Autenticación | Completa | JWT + 2FA |
| Suite pytest (`QA/`) | Automatizada | ~54 passed, 1 xfail (citas) |
| QA Postman / Newman | Funcional | Ver `QA/README.md` |
| Frontend UI | En progreso | HTML/CSS/JS estático |
| Base de Datos | PostgreSQL | Scripts en `database/` |
| Docker | Configurado | `docker-compose.yml` |
| Documentación | Actualizada | README + `QA/` |

Incidencias conocidas del API: [`QA/BACKEND_ISSUES_DETECTED.md`](QA/BACKEND_ISSUES_DETECTED.md).

## **Propuesta de Valor**

SIGI-A transforma la gestión tradicional de centros de estética en una **experiencia digital moderna**, permitiendo:

- **Escala**: Conecta múltiples negocios en una plataforma
- **Eficiencia**: Automatiza procesos manuales
- **Accesibilidad**: Acceso 24/7 desde cualquier dispositivo
- **Crecimiento**: Herramientas analíticas para tomar decisiones

---

## 🧪 **Testing**

### **Suite pytest (recomendado)**

```powershell
cd QA
pip install -r ..\backend\requirements.txt -r requirements-ci.txt
.\qa.ps1 check
```

Equivalente manual:

```bash
cd QA
python -m pytest tests -v --tb=short
python scripts/validate_postman_workspace.py
```

Los tests importan `app` desde `../backend` vía `QA/pytest.ini` y usan SQLite en memoria (`QA/tests/conftest.py`).

### **Postman y Newman**

- Colección YAML: `QA/postman/collections/SIGI-A/`
- Smoke Newman: `cd QA` → `.\qa.ps1 smoke` (API levantada)
- Guías: [`QA/postman/README.md`](QA/postman/README.md), [`QA/postman/newman/README.md`](QA/postman/newman/README.md)

---

## 🔐 **Seguridad**

### **Autenticación**
- **JWT**: Access y refresh tokens
- **2FA**: Verificación por email
- **Password Hashing**: bcrypt
- **Rate Limiting**: Protección anti bruteforce

### **Autorización**
- **Roles**: cliente, negocio, admin
- **Ownership**: Solo dueños pueden modificar sus recursos cuando aplica

### **Validaciones**
- **Pydantic**: Validación automática de tipos
- **SQLAlchemy**: Constraints a nivel de base de datos

---

## 🚀 **Despliegue**

### **Docker (recomendado)**

```bash
docker-compose up -d postgres
docker-compose up --build
```

- Backend: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

### **Variables de entorno**

```bash
cp .env.example .env
# Completar DATABASE_URL, SECRET_KEY, SMTP, etc.
```

---

## 📝 **Próximos pasos**

1. **Frontend**: Mejorar UX e integración con la API
2. **Backend**: Resolver incidencias documentadas en QA (p. ej. citas)
3. **CI/CD**: Ampliar pipelines según entorno de despliegue
4. **Producción**: Monitoring, caché y despliegue en cloud

---

## Referencias

| Tema | Documento |
|------|-----------|
| API backend | `backend/README.md` |
| Tests y Postman | `QA/README.md` |
| Guía pytest paso a paso | `QA/GUIA_TESTS.md` |
| Bugs reproducibles | `QA/BACKEND_ISSUES_DETECTED.md` |
