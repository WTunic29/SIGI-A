# SIGI-A

Esta carpeta contiene todas las herramientas de testing y calidad para el proyecto **SIGI-A (Sistema de Gestión Inteligente de Estética)**.

---

## Acerca de SIGI-A

SIGI-A es una plataforma completa que conecta múltiples negocios de estética (barberías, peluquerías, tatuajes, centros de belleza, etc.) en un solo sistema.

### Para Usuarios:
- Ver negocios cercanos
- Agendar citas
- Calificar servicios
- Comprar servicios/productos

### Para Negocios:
- Gestionar empleados
- Administrar citas en tiempo real
- Controlar inventario
- Ver reportes y métricas

---

## Arquitectura del Proyecto

```
SIGI-A/
├── backend/                    # API REST (FastAPI + PostgreSQL)
│   ├── app/
│   │   ├── core/              # Seguridad, dependencias, roles
│   │   ├── models/            # Modelos de base de datos (SQLAlchemy)
│   │   ├── routes/            # Endpoints de la API
│   │   ├── schemas/           # Validaciones (Pydantic)
│   │   ├── utils/             # Utilidades (email, seguridad)
│   │   ├── database.py        # Conexión a PostgreSQL
│   │   └── main.py            # Punto de entrada
│   ├── .env.example
│   └── README.md
├── frontend/                   # Interfaz web estática
│   ├── CSS/
│   ├── JS/
│   ├── SIGI-E/
│   └── index.html
├── QA/                         # Testing y Calidad
│   ├── .postman/              # Configuración interna de Postman
│   ├── postman/               # Colecciones, entornos y globals
│   └── README.md              # Este archivo
├── database/                   # Scripts SQL
│   ├── schema_actual.sql      # Esquema de base de datos
│   └── seeds_actual.sql       # Datos de prueba
├── .env.example               # Variables de entorno
├── .gitignore
├── README.md                  # Documentación principal
└── requirements.txt           # Dependencias Python
```

---

## Herramientas de Testing

### Postman Collections

Esta carpeta contiene las colecciones completas de Postman para probar todos los endpoints de la API.

#### Estructura de QA:

```
QA/
├── .postman/                  # Archivos internos de Postman
│   ├── .gitkeep
│   └── resources.yaml
└── postman/                   # Archivos exportados
    ├── collections/           # Colecciones de requests
    │   └── SIGI-A/           # Colección principal
    │       ├── Calificaciones/
    │       ├── Citas/
    │       ├── Empleados/
    │       ├── Health/
    │       ├── Negocios/
    │       ├── Notificaciones/
    │       ├── Pagos/
    │       ├── Pedidos/
    │       ├── Productos/
    │       ├── Servicios/
    │       └── Usuarios/
    ├── environments/          # Entornos de testing
    │   └── SIGI-A-Local.env.yaml
    └── globals/               # Variables globales
        └── workspace.globals.yaml
```

---

## Configuración de Testing

### 1. Instalar Postman

Descargar e instalar Postman desde: https://www.postman.com/downloads/

### 2. Importar Colecciones

1. Abrir Postman
2. Hacer clic en "Import" (arriba izquierda)
3. Seleccionar "File/Folder"
4. Navegar a `QA/postman/collections/`
5. Importar la colección `SIGI-A/`

### 3. Importar Entorno

1. En Postman, hacer clic en "Environments" (izquierda)
2. Hacer clic en "Import"
3. Importar `QA/postman/environments/SIGI-A-Local.env.yaml`

### 4. Configurar Variables

Revisar y actualizar las variables del entorno:
- `base_url`: URL del backend (ej: `http://127.0.0.1:8000`)
- `token`: Token JWT (se actualiza automáticamente)
- Credenciales de prueba

---

## Flujo de Testing

### 1. Health Check
- **GET** `/` - Verificar que el backend esté corriendo
- **GET** `/test-db` - Verificar conexión a base de datos

### 2. Autenticación
- **POST** `/auth/register` - Crear usuario de prueba
- **POST** `/auth/login` - Iniciar sesión (envía código 2FA)
- **POST** `/auth/verify-2fa` - Verificar código 2FA

### 3. Funcionalidades Principales
- **GET** `/auth/me` - Obtener usuario autenticado
- **POST** `/negocios/` - Crear negocio (solo rol "negocio")
- **GET** `/negocios/` - Listar negocios

### 4. Gestión de Negocios
- Empleados, servicios, productos, citas, etc.

---

## Variables de Entorno para Testing

```yaml
# QA/postman/environments/SIGI-A-Local.env.yaml
{
  "id": "sigia-local",
  "name": "SIGI-A Local",
  "values": [
    {
      "key": "base_url",
      "value": "http://127.0.0.1:8000",
      "enabled": true
    },
    {
      "key": "token",
      "value": "",
      "enabled": true
    }
  ]
}
```

---

## Ejecutar Tests

### Backend debe estar corriendo:

```bash
cd backend
uvicorn app.main:app --reload
```

### Ejecutar colección en Postman:

1. Seleccionar entorno "SIGI-A Local"
2. Abrir colección "SIGI-A"
3. Ejecutar requests en orden
4. Verificar respuestas y códigos de estado

---

## Notas de Testing

- **2FA**: El login requiere verificación por correo electrónico
- **Roles**: Algunos endpoints requieren rol específico ("cliente" o "negocio")
- **JWT**: Mantener token actualizado en variables de entorno
- **Base de datos**: Asegurar que el schema esté aplicado antes de testing

---

## Soporte

Para preguntas sobre testing o la API, revisar:
- `backend/README.md` - Documentación técnica del backend
- `README.md` - Documentación general del proyecto
- Documentación Swagger: `http://127.0.0.1:8000/docs`
