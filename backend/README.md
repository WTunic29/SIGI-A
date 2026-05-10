🚀 SIGI-A Backend

Backend oficial de SIGI-A (Sistema de Gestión Inteligente de Estética).

SIGI-A es una plataforma tipo marketplace enfocada en:

barberías
estéticas
tatuajes
spa
negocios de belleza y bienestar

El sistema permite:

autenticación segura
gestión de negocios
gestión de empleados
servicios
citas
inventario
pedidos
pagos
carrito
favoritos
notificaciones
auditoría
control de sesiones
seguridad enterprise
🧱 Stack Tecnológico
Backend
Python 3
FastAPI
SQLAlchemy
PostgreSQL
Seguridad
JWT
Refresh Tokens
2FA por correo
bcrypt
Rate Limiting
Ownership Validation
Control de Sesiones
Roles y permisos
Utilidades
SMTP
dotenv
Swagger/OpenAPI
📂 Arquitectura del Proyecto
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
⚙️ Instalación del Proyecto
1. Clonar repositorio
git clone https://github.com/WTunic29/SIGI-A.git
2. Entrar al backend
cd SIGI-A/backend
3. Crear entorno virtual
Windows
python -m venv venv
4. Activar entorno virtual
Windows
venv\Scripts\activate
Linux / Mac
source venv/bin/activate
5. Instalar dependencias
pip install -r requirements.txt
6. Configurar variables de entorno

Crear archivo:

.env

Ejemplo:

DATABASE_URL=postgresql://postgres:password@localhost:5432/sigi_a

SECRET_KEY=TU_SECRET_KEY

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

REFRESH_TOKEN_EXPIRE_DAYS=7

EMAIL_USER=correo@gmail.com

EMAIL_PASSWORD=password_app_gmail
▶️ Ejecutar Backend
uvicorn app.main:app --reload
🌐 URLs importantes
Backend
http://127.0.0.1:8000
Swagger
http://127.0.0.1:8000/docs
🗄️ Base de Datos
Motor
PostgreSQL
Schema principal
core
📋 Módulos Implementados
Autenticación
Login
Register
JWT
Refresh Token
Logout
2FA
Sesiones activas
Negocios
CRUD negocios
Ownership validation
Protección por roles
Servicios
CRUD servicios
Seguridad por negocio
Empleados
CRUD empleados
Horarios
Servicios asignados
Citas
Gestión completa de citas
Detalle de cita
Seguridad cliente/negocio
Productos
CRUD productos
Inventario
Movimientos stock
Pedidos
Pedidos
Detalle pedido
Carrito
Favoritos
Otros módulos
Pagos
Auditoría
Notificaciones
Recuperación contraseña
Sesiones
🔐 Seguridad Implementada
JWT Authentication

El backend usa:

access token
refresh token
2FA

Durante login:

usuario ingresa credenciales
sistema genera código
código enviado por correo
usuario valida código
backend entrega JWT
Roles

Roles soportados:

cliente
negocio
admin
Ownership Validation

El sistema valida:

clientes solo ven sus recursos
negocios solo administran SU información
admin puede acceder globalmente

Ejemplos:

negocio no puede editar productos de otro negocio
cliente no puede ver citas de otro cliente
Rate Limiting

Protección anti bruteforce:

login limitado
verify-2fa limitado
refresh limitado
Password Hashing

Contraseñas protegidas con:

bcrypt
passlib
Sesiones

Se registran:

token
IP
user-agent
expiración
estado sesión
🔄 Flujo de Autenticación
1. Login
Endpoint
POST /auth/login
Body
{
  "correo": "usuario@email.com",
  "password": "123456"
}
2. Verificación 2FA
Endpoint
POST /auth/verify-2fa
Body
{
  "correo": "usuario@email.com",
  "codigo": "123456"
}
3. Respuesta JWT
{
  "access_token": "TOKEN",
  "refresh_token": "TOKEN",
  "token_type": "bearer"
}
4. Uso JWT
Authorization: Bearer TOKEN
5. Refresh Token
POST /auth/refresh
6. Logout
POST /auth/logout

Invalida sesiones activas.

📡 Swagger

Swagger/OpenAPI disponible en:

/docs

Permite:

probar endpoints
autenticación Bearer
pruebas backend
🚀 Estado Actual
Backend

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

📌 Próximos Pasos
Frontend
Login UI
Dashboard negocio
Dashboard cliente
Marketplace
Producción
Docker
HTTPS
Deploy cloud
Nginx
Swagger OFF producción
CI/CD
👨‍💻 Equipo de Desarrollo
Brandon Esteban Melo Bolaños
Paula Andrea Villada Álvarez
Diego Alejandro Betancur Herrera
Christian Camilo Lopez