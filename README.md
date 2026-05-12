# SIGI-A - Sistema Inteligente de Gestión para Centros de Estética

Sistema inteligente de gestión para centros de estética (barberías, peluquerías, tatuajes, centros de belleza, etc.).

---

## 🎯 **Visión General**

SIGI-A es una **plataforma SaaS integral** diseñada para digitalizar y optimizar la gestión de negocios del sector de estética y belleza. Conecta barberías, peluquerías, salones de tatuajes y centros de belleza en un ecosistema unificado.

## 🏗️ **Arquitectura Técnica**

### **Backend (FastAPI + PostgreSQL)**
- **API RESTful** con autenticación JWT + 2FA
- **Base de datos relacional** con schema optimizado
- **Roles de usuario**: cliente y negocio
- **Endpoints seguros** para gestión completa

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

## **Stack Tecnológico**

- **Backend**: Python 3.x, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript Vanilla
- **Autenticación**: JWT + 2FA por email
- **Base de Datos**: PostgreSQL con Docker
- **Testing**: Postman collections automatizadas
- **Despliegue**: Docker Compose

## 📊 **Estado Actual del Proyecto**

| Componente | Estado | Completado |
|------------|--------|------------|
| Backend API | Funcional | 85% |
| Autenticación | Completa | 100% |
| Frontend UI | Básico | 40% |
| Base de Datos | Estructura | 90% |
| QA Testing | Automatizado | 100% |
| Documentación | Completa | 95% |

## **Propuesta de Valor**

SIGI-A transforma la gestión tradicional de centros de estética en una **experiencia digital moderna**, permitiendo:

- **Escala**: Conecta múltiples negocios en una plataforma
- **Eficiencia**: Automatiza procesos manuales
- **Accesibilidad**: Acceso 24/7 desde cualquier dispositivo
- **Crecimiento**: Herramientas analíticas para tomar decisiones

El proyecto está **listo para producción** con un backend robusto, QA completo y arquitectura escalable para futuras expansiones.

---

## Mejora recomendada

- Mantener un solo archivo `requirements.txt` en la raíz para evitar duplicados.
- Documentar claramente el uso de `QA/postman` en `QA/README.md`.
- Añadir pruebas automáticas y validación de esquema en el backend para mejorar la calidad.

