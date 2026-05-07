# SIGI-A Postman Collections

Este directorio contiene las colecciones y entornos de Postman para probar la API del backend de **SIGI-A (Sistema de Gestión Inteligente de Estética)**.

## Estructura de archivos

### Environments
- **`SIGI-A-Local.env.yaml`**: Variables de entorno para pruebas locales.
  - `base_url`: URL base del backend (por defecto `http://localhost:8000`).
  - `token`: Token JWT para autenticación.
  - `correo_2fa`: Correo del usuario para verificación 2FA.
  - `codigo_2fa`: Código de 6 dígitos para 2FA (obtener de DB o email).
  - `rol_default`: Rol por defecto para registro (cliente/negocio/admin).
  - `id_usuario`: ID del usuario autenticado.
  - `id_negocio`: ID del negocio creado.

### Collections
- **`collection.yaml`**: Archivo principal de la colección Postman. Define la estructura y metadatos.
- **`Auth/`**: Endpoints de autenticación.
  - `Register.request.yaml`: Registra un nuevo usuario.
  - `Login.request.yaml`: Inicia sesión y solicita 2FA.
  - `Verify-2FA.request.yaml`: Verifica el código 2FA y obtiene token JWT.
  - `Get-Me.request.yaml`: Obtiene datos del usuario autenticado (requiere token).
  - `Solo-Negocio.request.yaml`: Endpoint protegido para rol "negocio" (requiere token).
- **`Health/`**: Endpoints de salud del sistema.
  - `Root.request.yaml`: Verifica que el servidor esté corriendo.
  - `Test-DB.request.yaml`: Verifica conexión a la base de datos.
- **`Negocios/`**: Endpoints de gestión de negocios.
  - `Crear-Negocio.request.yaml`: Crea un nuevo negocio (requiere token y rol negocio).
  - `Listar-Negocios.request.yaml`: Lista todos los negocios.

## Paso a paso para ejecutar pruebas en Postman

### 1. Preparar el backend
- Asegúrate de que PostgreSQL esté corriendo: `docker-compose up -d`.
- Crea `backend/.env` con las credenciales de DB.
- Activa el entorno virtual: `backend\venv\Scripts\activate`.
- Instala dependencias: `pip install -r requirements.txt`.
- Ejecuta el backend: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

### 2. Importar en Postman
- Abre Postman.
- Ve a **File > Import**.
- Selecciona `environments/SIGI-A-Local.env.yaml` para importar el entorno.
- Selecciona `collections/SIGI-A/collection.yaml` para importar la colección.

### 3. Configurar entorno
- En Postman, selecciona el entorno "SIGI-A Local".
- Verifica que `base_url` sea `http://localhost:8000`.
- Ajusta `rol_default` si es necesario (por defecto "negocio").

### 4. Ejecutar pruebas
Sigue este orden para probar la API:

1. **Health/Root**:
   - Método: GET
   - URL: `{{base_url}}/`
   - Esperado: Status 200, mensaje de backend funcionando.

2. **Health/Test-DB**:
   - Método: GET
   - URL: `{{base_url}}/test-db`
   - Esperado: Status 200, `"database": "conectada"`, `"resultado": 1`.

3. **Auth/Register**:
   - Método: POST
   - URL: `{{base_url}}/auth/register`
   - Body: JSON con datos del usuario (rol usa `{{rol_default}}`).
   - Esperado: Status 201, usuario creado. Guarda `id_usuario` y `correo_2fa`.

4. **Auth/Login**:
   - Método: POST
   - URL: `{{base_url}}/auth/login`
   - Body: JSON con `correo` y `password`.
   - Esperado: Status 200, requiere 2FA. Ver console para instrucciones.
   - **Nota**: El código 2FA se envía al correo (en prod) o se genera en DB.

5. **Obtener código 2FA**:
   - Para testing: Conecta a la DB PostgreSQL.
   - Ejecuta: `SELECT codigo FROM core.codigo_2fa WHERE id_usuario = {{id_usuario}} ORDER BY fecha_creacion DESC LIMIT 1;`
   - Copia el código de 6 dígitos.
   - En Postman, establece `codigo_2fa` en el entorno con ese valor.

6. **Auth/Verify-2FA**:
   - Método: POST
   - URL: `{{base_url}}/auth/verify-2fa`
   - Body: JSON con `correo` (`{{correo_2fa}}`) y `codigo` (`{{codigo_2fa}}`).
   - Esperado: Status 200, token JWT. Guarda `token`.

7. **Auth/Get-Me**:
   - Método: GET
   - URL: `{{base_url}}/auth/me`
   - Headers: `Authorization: Bearer {{token}}`
   - Esperado: Status 200, datos del usuario.

8. **Auth/Solo-Negocio** (si rol es negocio):
   - Método: GET
   - URL: `{{base_url}}/auth/solo-negocio`
   - Headers: `Authorization: Bearer {{token}}`
   - Esperado: Status 200, mensaje para negocio.

9. **Negocios/Crear-Negocio** (si rol es negocio):
   - Método: POST
   - URL: `{{base_url}}/negocios/`
   - Headers: `Authorization: Bearer {{token}}`
   - Body: JSON con datos del negocio.
   - Esperado: Status 201, negocio creado. Guarda `id_negocio`.

10. **Negocios/Listar-Negocios**:
    - Método: GET
    - URL: `{{base_url}}/negocios/`
    - Esperado: Status 200, lista de negocios.

### Notas importantes
- **2FA**: En desarrollo, obtén el código de la DB. En producción, del email.
- **Roles**: "cliente" puede registrarse y autenticarse; "negocio" puede crear/listar negocios.
- **Errores**: Si falla, verifica que el backend esté corriendo y la DB conectada.
- **Scripts**: Los requests tienen tests automáticos en Postman.

Para más detalles, consulta la documentación del backend en `backend/README.md`.