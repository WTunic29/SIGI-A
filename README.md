# SIGI-A - Sistema Inteligente de Gestión para Centros de Estética

Sistema inteligente de gestión para centros de estética (barberías, peluquerías, tatuajes, centros de belleza, etc.).

---

## 🎯 **Visión General**

SIGI-A es una **plataforma SaaS integral** diseñada para digitalizar y optimizar la gestión de negocios del sector de estética y belleza. Conecta barberías, peluquerías, salones de tatuajes y centros de belleza en un ecosistema unificado.

## Carrito unificado (productos + citas → pago → factura)

Flujo implementado para que el cliente agregue **productos** y **servicios agendados** al mismo carrito, pague en un solo checkout y reciba **factura imprimible**.

Documentación completa (arquitectura, diagramas, API, despliegue Linux/AWS): **[docs/CARRITO_UNIFICADO.md](docs/CARRITO_UNIFICADO.md)**

## 🏗️ **Arquitectura Técnica**

### **Backend (FastAPI + PostgreSQL)**
- **API RESTful** con autenticación JWT + 2FA
- **Base de datos relacional** con schema optimizado
<<<<<<< HEAD
- **Roles de usuario**: cliente y negocio
- **Endpoints seguros** para gestión completa
=======
- **Roles de usuario**: cliente, negocio, admin
- **22 modelos SQLAlchemy** con relaciones enterprise
- **20 schemas Pydantic** para validación automática
- **21 endpoints FastAPI** con seguridad completa
- **Testing profesional** con pytest y coverage
>>>>>>> 869846f79e1f83ea6e29e19282cdebe9458cd5a1

### **Frontend (Web)**
- **Interfaz responsiva** HTML/CSS/JavaScript
- **Dashboard diferenciado** por rol
- **Gestión visual** de citas y servicios
- **Experiencia móvil-friendly**

### **QA & Testing**
- **Postman collections** 100% funcionales
- **9 endpoints automatizados**
- **Validaciones completas** de API
- **Flujo de testing** documentado
<<<<<<< HEAD
=======
- **Suite pytest profesional** para backend
>>>>>>> 869846f79e1f83ea6e29e19282cdebe9458cd5a1

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

<<<<<<< HEAD
## Estructura del proyecto

```
SIGI-A/
├── backend/
│   ├── app/               # Código del backend (FastAPI)
│   ├── .env.example       # Ejemplo de variables de entorno del backend
│   └── README.md          # Documentación del backend
├── frontend/              # Archivos estáticos e interfaz
│   ├── CSS/
│   ├── JS/
│   ├── SIGI-E/
│   └── index.html
├── QA/                    # Postman y pruebas de API
│   ├── .postman/
│   ├── postman/
│   └── README.md
├── database/              # Scripts SQL
│   ├── schema_actual.sql
│   └── seeds_actual.sql
├── .env.example           # Variables de entorno generales
├── .gitignore
├── README.md
└── requirements.txt       # Dependencias Python
=======
## 📁 **Estructura del Proyecto**

```
SIGI-A/
│
├── backend/                 # API FastAPI + PostgreSQL
│   ├── app/                # Aplicación principal
│   │   ├── models/         # 22 modelos SQLAlchemy
│   │   ├── schemas/        # 20 schemas Pydantic
│   │   ├── routes/         # 21 endpoints FastAPI
│   │   ├── core/           # Configuración central
│   │   ├── utils/          # Seguridad y utilidades
│   │   ├── middleware/     # Middleware personalizado
│   │   ├── database.py     # Configuración BD
│   │   └── main.py         # Aplicación FastAPI
│   │
│   ├── tests/              # Suite testing profesional
│   │   ├── test_models/    # Tests de persistencia
│   │   ├── test_schemas/   # Tests de validación
│   │   ├── test_routes/    # Tests de API
│   │   ├── conftest.py     # Configuración pytest
│   │   └── pytest.ini     # Configuración testing
│   │
│   ├── requirements.txt    # Dependencias Python
│   ├── Dockerfile         # Contenedor backend
│   ├── .env.example       # Variables de entorno
│   └── README.md          # Documentación backend
│
├── frontend/              # Interfaz web (HTML/CSS/JS)
│   ├── CSS/               # Estilos responsivos
│   ├── JS/                # Lógica del frontend
│   ├── SIGI-E/            # Componentes UI
│   └── index.html         # Página principal
│
├── QA/                    # Testing con Postman
│   ├── postman/           # Collections automatizadas
│   ├── .postman/          # Configuración Postman
│   └── README.md          # Documentación QA
│
├── database/              # Scripts base de datos
│   ├── schema_actual.sql  # Estructura actual
│   └── seeds_actual.sql   # Datos iniciales
│
├── scripts/               # Scripts mantenimiento
├── docker-compose.yml     # Orquestación contenedores
├── docker-compose.dev.yml # Configuración desarrollo
├── .env.example          # Variables entorno generales
├── .gitignore
├── requirements.txt       # Dependencias Python
└── README.md             # Documentación general
>>>>>>> 869846f79e1f83ea6e29e19282cdebe9458cd5a1
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

Crear un archivo `.env` basado en `.env.example` y completar los valores.

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

<<<<<<< HEAD
## **Stack Tecnológico**

- **Backend**: Python 3.x, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript Vanilla
- **Autenticación**: JWT + 2FA por email
- **Base de Datos**: PostgreSQL con Docker
- **Testing**: Postman collections automatizadas
- **Despliegue**: Docker Compose
=======
## 🛠️ **Stack Tecnológico**

### **Backend**
- **Framework**: Python 3.11+, FastAPI
- **ORM**: SQLAlchemy 2.0
- **Base de Datos**: PostgreSQL 16 con schema `core`
- **Validación**: Pydantic v2
- **Testing**: pytest + pytest-cov (coverage)

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
- **Testing QA**: Postman collections automatizadas
- **Documentación**: Swagger/OpenAPI
- **Logging**: Middleware personalizado
>>>>>>> 869846f79e1f83ea6e29e19282cdebe9458cd5a1

## 📊 **Estado Actual del Proyecto**

| Componente | Estado | Completado |
|------------|--------|------------|
<<<<<<< HEAD
| Backend API | Funcional | 85% |
| Autenticación | Completa | 100% |
| Frontend UI | Básico | 40% |
| Base de Datos | Estructura | 90% |
| QA Testing | Automatizado | 100% |
| Documentación | Completa | 95% |
=======
| Backend API | ✅ Enterprise | 100% |
| Models SQLAlchemy | ✅ Completo | 22/22 |
| Schemas Pydantic | ✅ Completo | 20/20 |
| Routes FastAPI | ✅ Completo | 21/21 |
| Testing Suite | ✅ Profesional | 100% |
| Autenticación | ✅ JWT + 2FA | 100% |
| Frontend UI | 🔄 Básico | 60% |
| Base de Datos | ✅ PostgreSQL | 100% |
| QA Postman | ✅ Funcional | 100% |
| Docker Config | ✅ Listo | 100% |
| Documentación | ✅ Completa | 100% |
>>>>>>> 869846f79e1f83ea6e29e19282cdebe9458cd5a1

## **Propuesta de Valor**

SIGI-A transforma la gestión tradicional de centros de estética en una **experiencia digital moderna**, permitiendo:

- **Escala**: Conecta múltiples negocios en una plataforma
- **Eficiencia**: Automatiza procesos manuales
- **Accesibilidad**: Acceso 24/7 desde cualquier dispositivo
- **Crecimiento**: Herramientas analíticas para tomar decisiones

El proyecto está **listo para producción** con un backend robusto, QA completo y arquitectura escalable para futuras expansiones.

---

<<<<<<< HEAD
## Mejora recomendada

- Mantener un solo archivo `requirements.txt` en la raíz para evitar duplicados.
- Documentar claramente el uso de `QA/postman` en `QA/README.md`.
- Añadir pruebas automáticas y validación de esquema en el backend para mejorar la calidad.
=======
## 🧪 **Testing Profesional**

### **Backend Testing Suite**
```bash
# Ejecutar todos los tests
cd backend
pytest -v --cov=app --cov-report=html

# Tests por categoría
pytest tests/test_models/ -v      # Tests de persistencia
pytest tests/test_schemas/ -v     # Tests de validación
pytest tests/test_routes/ -v      # Tests de API

# Coverage report
pytest --cov=app --cov-report=term-missing
```

### **QA con Postman**
- Importar collections desde `QA/postman/collections/`
- Importar entorno desde `QA/postman/environments/`
- 9 endpoints automatizados 100% funcionales
- Validaciones completas de API

### **Características de Testing**
- **Base de datos temporal**: SQLite en memoria
- **Fixtures reutilizables**: Usuarios autenticados, datos de prueba
- **Override de dependencias**: Base de datos aislada
- **Coverage**: Medición de cobertura de código
- **Autenticación JWT mock**: Tokens de prueba

---

## 🔐 **Seguridad Enterprise**

### **Autenticación**
- **JWT**: Access y refresh tokens
- **2FA**: Verificación por email
- **Password Hashing**: bcrypt
- **Rate Limiting**: Protección anti bruteforce

### **Autorización**
- **Roles**: cliente, negocio, admin
- **Ownership Validation**: Solo dueños pueden modificar sus recursos
- **Middleware**: Security headers y logs

### **Validaciones**
- **Pydantic**: Validación automática de tipos
- **SQLAlchemy**: Constraints a nivel de base de datos
- **Sanitización**: Inputs seguros

---

## 🚀 **Despliegue y Producción**

### **Docker (Recomendado)**
```bash
# Backend con PostgreSQL
docker-compose up -d postgres
docker-compose up --build

# Acceso a servicios
# Backend: http://127.0.0.1:8000
# Swagger: http://127.0.0.1:8000/docs
```

### **Variables de Entorno**
```bash
# Copiar y configurar
cp .env.example .env
cp backend/.env.example backend/.env

# Variables principales
DATABASE_URL=postgresql://user:pass@localhost:5432/sigi
SECRET_KEY=tu-secret-key
EMAIL_USER=tu-email@gmail.com
EMAIL_PASSWORD=tu-app-password
```

---

## 📝 **Próximos Pasos**

1. **Frontend Avanzado**: React/Vue para mejor UX
2. **CI/CD Pipeline**: GitHub Actions o GitLab CI
3. **Monitoring**: Logs y métricas con Grafana/Prometheus
4. **Performance**: Caching con Redis y optimización
5. **Deploy Cloud**: AWS, Azure o Google Cloud

---

## 🎯 **Propuesta de Valor**

SIGI-A transforma la gestión tradicional de centros de estética en una **experiencia digital moderna**, permitiendo:

- **Escala**: Conecta múltiples negocios en una plataforma
- **Eficiencia**: Automatiza procesos manuales
- **Accesibilidad**: Acceso 24/7 desde cualquier dispositivo
- **Crecimiento**: Herramientas analíticas para tomar decisiones

**El proyecto está listo para producción con un backend enterprise-ready, testing completo y arquitectura escalable.** 🚀
>>>>>>> 869846f79e1f83ea6e29e19282cdebe9458cd5a1

