# SIGI-A

Sistema inteligente de gestión para centros de estética (barberías, peluquerías, tatuajes, centros de belleza, etc.).

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

## Mejora recomendada

- Mantener un solo archivo `requirements.txt` en la raíz para evitar duplicados.
- Documentar claramente el uso de `QA/postman` en `QA/README.md`.
- Añadir pruebas automáticas y validación de esquema en el backend para mejorar la calidad.

