# 🚀 SIGI-A Backend

Backend del sistema **SIGI-A (Sistema de Gestión Inteligente de Estética)**, desarrollado con **FastAPI** y **PostgreSQL**.

Este backend permite la gestión de usuarios (clientes y negocios), autenticación segura con **JWT**, y verificación en dos pasos (**2FA por correo**).

---

## 🧱 Tecnologías utilizadas

* Python 3.x
* FastAPI
* PostgreSQL
* SQLAlchemy
* JWT (Autenticación)
* Passlib (Encriptación de contraseñas)
* SMTP (Envío de correos - 2FA)

---

## 📂 Estructura del proyecto

```
backend/
├── app/               # Código del backend (FastAPI)
│   ├── core/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── utils/
│   ├── database.py
│   └── main.py
├── .env.example
└── README.md
```

---

## ⚙️ Configuración del entorno

### 1. Crear entorno virtual

```bash
python -m venv venv
```

### 2. Activar entorno virtual

**Windows:**

```bash
venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

Desde la raíz del proyecto:

```bash
pip install -r requirements.txt
```

O desde la carpeta `backend`:

```bash
pip install -r ../requirements.txt
```

---

### 4. Configurar variables de entorno

Copiar `.env.example` y crear un archivo `.env` con los valores reales:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/sigi_a
SECRET_KEY=tu_clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## ▶️ Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

El backend estará disponible en `http://127.0.0.1:8000`.

---

## 🌐 URLs importantes

* Backend: `http://127.0.0.1:8000`
* Documentación Swagger: `http://127.0.0.1:8000/docs`

---

## 🔐 Autenticación y Seguridad

El sistema implementa:

* Contraseñas encriptadas
* Autenticación con JWT
* Protección de rutas
* Roles (cliente / negocio)
* Verificación en dos pasos (2FA por correo)

---

## 🔄 Flujo de autenticación

### 1. Login

**POST** `/auth/login`

Body:

```json
{
  "correo": "usuario@email.com",
  "password": "123456"
}
```

Respuesta:

```json
{
  "message": "Código 2FA enviado al correo",
  "requiere_2fa": true,
  "correo": "usuario@email.com"
}
```

---

### 2. Verificación 2FA

**POST** `/auth/verify-2fa`

Body:

```json
{
  "correo": "usuario@email.com",
  "codigo": "123456"
}
```

Respuesta:

```json
{
  "message": "2FA validado correctamente",
  "access_token": "TOKEN",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "nombre": "...",
    "correo": "...",
    "rol": "cliente"
  }
}
```

---

### 3. Uso del token

Guardar el token en el frontend:

```js
localStorage.setItem("token", access_token)
```

Enviar en cada petición protegida:

```http
Authorization: Bearer TOKEN
```

---

### 4. Obtener usuario autenticado

**GET** `/auth/me`


Header:

```
Authorization: Bearer TOKEN
```

Respuesta:

```
{
  "id": 1,
  "nombre": "...",
  "correo": "...",
  "rol": "cliente"
}
```

---

## 👥 Roles

El sistema maneja dos tipos de usuarios:

* `cliente`
* `negocio`

El frontend debe redirigir según el rol después del login.

---

## ⚠️ Notas importantes

* El código 2FA expira en 5 minutos
* Cada código solo puede usarse una vez
* El backend permite conexiones desde frontend (CORS habilitado)
* No subir el archivo `.env` ni la carpeta `venv/` al repositorio

---

## 👨‍💻 Equipo de desarrollo

* Brandon Esteban Melo Bolaños
* Paula Andrea Villada Álvarez
* Diego Alejandro Betancur Herrera
* Christian Camilo Lopez

---

## 📌 Estado del proyecto

✔ Backend funcional
✔ Autenticación completa (JWT + 2FA)
✔ Listo para integración con frontend

---

## 🚀 Próximos pasos

* Integración con frontend
* Panel de cliente
* Panel de negocio
* Gestión de citas
* Inventario y servicios

```
```
