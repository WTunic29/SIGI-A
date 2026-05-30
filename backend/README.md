# 🚀 SIGI-A Backend

Backend oficial de **SIGI-A (Sistema de Gestión Inteligente de Estética)**.

SIGI-A es una plataforma tipo marketplace enfocada en:

* barberías
* estéticas
* tatuajes
* spa
* negocios de belleza y bienestar

El sistema permite:

* autenticación segura
* gestión de negocios
* gestión de empleados
* servicios
* citas
* inventario
* pedidos
* pagos
* carrito
* favoritos
* notificaciones
* auditoría
* control de sesiones
* seguridad enterprise

---

# 🧱 Stack Tecnológico

## Backend

* Python 3
* FastAPI
* SQLAlchemy
* PostgreSQL

## Seguridad

* JWT
* Refresh Tokens
* 2FA por correo
* bcrypt
* Rate Limiting
* Ownership Validation
* Control de Sesiones
* Roles y permisos

## Utilidades

* SMTP
* dotenv
* Swagger/OpenAPI

---

# 📂 Arquitectura del Proyecto

```bash
backend/
│
├── app/
│   ├── core/
│   │   ├── deps.py
│   │   └── rate_limit.py
│   │
│   ├── models/
│   │
│   ├── routes/
│   │
│   ├── schemas/
│   │
│   ├── utils/
│   │   ├── security.py
│   │   └── email.py
│   │
│   ├── database.py
│   └── main.py
│
├── venv/
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

---

# ⚙️ Instalación del Proyecto

## 1. Clonar repositorio

```bash
git clone https://github.com/WTunic29/SIGI-A.git
```

---

## 2. Entrar al backend

```bash
cd SIGI-A/backend
```

---

## 3. Crear entorno virtual

### Windows

```bash
python -m venv venv
```

---

## 4. Activar entorno virtual

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

## 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 6. Configurar variables de entorno

Crear archivo:

```bash
.env
```

Ejemplo:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/sigi_a

SECRET_KEY=TU_SECRET_KEY

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

REFRESH_TOKEN_EXPIRE_DAYS=7

EMAIL_USER=correo@gmail.com

EMAIL_PASSWORD=password_app_gmail
```

---

# ▶️ Ejecutar Backend

```bash
uvicorn app.main:app --reload
```

---

# 🌐 URLs importantes

## Backend

```bash
http://127.0.0.1:8000
```

## Swagger

```bash
http://127.0.0.1:8000/docs
```

---

# 🗄️ Base de Datos

## Motor

* PostgreSQL

## Schema principal

```sql
core
```

---

# 📋 Módulos Implementados

## Autenticación

* Login
* Register
* JWT
* Refresh Token
* Logout
* 2FA
* Sesiones activas

---

## Negocios

* CRUD negocios
* Ownership validation
* Protección por roles

---

## Servicios

* CRUD servicios
* Seguridad por negocio

---

## Empleados

* CRUD empleados
* Horarios
* Servicios asignados

---

## Citas

* Gestión completa de citas
* Detalle de cita
* Seguridad cliente/negocio

---

## Productos

* CRUD productos
* Inventario
* Movimientos stock

---

## Pedidos

* Pedidos
* Detalle pedido
* Carrito
* Favoritos

---

## Otros módulos

* Pagos
* Auditoría
* Notificaciones
* Recuperación contraseña
* Sesiones

---

# 🔐 Seguridad Implementada

## JWT Authentication

El backend usa:

* access token
* refresh token

---

## 2FA

Durante login:

1. usuario ingresa credenciales
2. sistema genera código
3. código enviado por correo
4. usuario valida código
5. backend entrega JWT

---

## Roles

Roles soportados:

```text
cliente
negocio
admin
```

---

## Ownership Validation

El sistema valida:

* clientes solo ven sus recursos
* negocios solo administran SU información
* admin puede acceder globalmente

Ejemplos:

* negocio no puede editar productos de otro negocio
* cliente no puede ver citas de otro cliente

---

## Rate Limiting

Protección anti bruteforce:

* login limitado
* verify-2fa limitado
* refresh limitado

---

## Password Hashing

Contraseñas protegidas con:

* bcrypt
* passlib

---

## Sesiones

Se registran:

* token
* IP
* user-agent
* expiración
* estado sesión

---

# 🔄 Flujo de Autenticación

## 1. Login

### Endpoint

```http
POST /auth/login
```

### Body

```json
{
  "correo": "usuario@email.com",
  "password": "123456"
}
```

---

## 2. Verificación 2FA

### Endpoint

```http
POST /auth/verify-2fa
```

### Body

```json
{
  "correo": "usuario@email.com",
  "codigo": "123456"
}
```

---

## 3. Respuesta JWT

```json
{
  "access_token": "TOKEN",
  "refresh_token": "TOKEN",
  "token_type": "bearer"
}
```

---

## 4. Uso JWT

```http
Authorization: Bearer TOKEN
```

---

## 5. Refresh Token

```http
POST /auth/refresh
```

---

## 6. Logout

```http
POST /auth/logout
```

Invalida sesiones activas.

---

# 📡 Swagger

Swagger/OpenAPI disponible en:

```bash
/docs
```

Permite:

* probar endpoints
* autenticación Bearer
* pruebas backend

---

# 🚀 Estado Actual

## Backend

✅ Arquitectura enterprise
✅ Seguridad avanzada
✅ JWT + Refresh Token
✅ 2FA
✅ Ownership Validation
✅ Roles y permisos
✅ Rate Limiting
✅ CRUD completos
✅ Swagger
✅ PostgreSQL
✅ Control sesiones
✅ Auditoría

---

# 📌 Próximos Pasos

## Frontend

* Login UI
* Dashboard negocio
* Dashboard cliente
* Marketplace

---

## Producción

* Docker
* HTTPS
* Deploy cloud
* Nginx
* Swagger OFF producción
* CI/CD

---

# 👨‍💻 Equipo de Desarrollo

* Brandon Esteban Melo B
