# SIGI-A Postman Collections

Esta carpeta contiene las colecciones y entornos de Postman **100% funcionales** para probar la API del backend de **SIGI-A (Sistema de Gestión Inteligente de Estética)**.

## Estructura Limpia

```
SIGI-A/
├── Auth/                    # Endpoints de autenticación
│   ├── Register.request.yaml
│   ├── Login.request.yaml
│   ├── Verify-2FA.request.yaml
│   ├── Get-Me.request.yaml
│   └── Solo-Negocio.request.yaml
├── Health/                  # Endpoints de salud
│   ├── Root.request.yaml
│   └── Test-DB.request.yaml
├── Negocios/               # Endpoints de negocios
│   ├── Crear-Negocio.request.yaml
│   └── Listar-Negocios.request.yaml
├── collection.yaml         # Colección principal
└── README.md              # Este archivo
```

## Archivos Funcionales

### Authentication Flow
1. **Register** → Crear usuario (POST `/auth/register`)
2. **Login** → Iniciar sesión (POST `/auth/login`)
3. **Verify-2FA** → Verificar código (POST `/auth/verify-2fa`)
4. **Get-Me** → Obtener perfil (GET `/auth/me`)
5. **Solo-Negocio** → Endpoint protegido (GET `/auth/solo-negocio`)

### Business Management
1. **Crear-Negocio** → Crear negocio (POST `/negocios/`)
2. **Listar-Negocios** → Listar negocios (GET `/negocios/`)

### Health Check
1. **Root** → Verificar backend (GET `/`)
2. **Test-DB** → Verificar DB (GET `/test-db`)

## Configuración del Entorno

### Variables Requeridas
- `base_url`: `http://localhost:8000`
- `token`: Token JWT (se llena automáticamente)
- `correo_2fa`: Correo para 2FA (se llena automáticamente)
- `codigo_2fa`: Código 2FA (manual desde DB)
- `rol_default`: `negocio` o `cliente`
- `id_usuario`: ID usuario (se llena automáticamente)
- `id_negocio`: ID negocio (se llena automáticamente)

## Flujo de Pruebas Completo

### 1. Preparación
```bash
# Iniciar PostgreSQL
docker-compose up -d

# Iniciar backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Importar en Postman
1. **File > Import**
2. Seleccionar `environments/SIGI-A-Local.env.yaml`
3. Seleccionar `collections/SIGI-A/collection.yaml`

### 3. Ejecutar Pruebas (Orden Recomendado)

**Health Check**
- Root → Test-DB

**Authentication**
- Register → Login → Verify-2FA → Get-Me → Solo-Negocio

**Business**
- Crear-Negocio → Listar-Negocios

## Obtener Código 2FA

Para pruebas manuales, consultar el código 2FA:

```sql
SELECT codigo, fecha_expiracion, usado 
FROM core.codigo_2fa 
WHERE id_usuario = [ID_USUARIO] 
ORDER BY id_codigo DESC 
LIMIT 1;
```

## Validaciones Automatizadas

### Status Codes
- **201**: Recurso creado exitosamente
- **200**: Operación exitosa
- **401**: No autorizado
- **400**: Bad Request
- **404**: No encontrado

### Response Structure
- **Auth**: `message`, `usuario` con campos completos
- **Business**: `message`, `negocio` con datos completos
- **Health**: `message`, `database`, `resultado`

## 📊 Cobertura de API

| Endpoint | Método | Estado | Tests |
|----------|--------|--------|-------|
| `/` | GET | Funcional | Status, Message |
| `/test-db` | GET | Funcional | Status, DB Connection |
| `/auth/register` | POST | Funcional | Status, User Creation |
| `/auth/login` | POST | Funcional | Status, 2FA Required |
| `/auth/verify-2fa` | POST | Funcional | Status, Token |
| `/auth/me` | GET | Funcional | Status, User Data |
| `/auth/solo-negocio` | GET | Funcional | Status, Role |
| `/negocios/` | POST | Funcional | Status, Business |
| `/negocios/` | GET | Funcional | Status, List |

**Total: 9 endpoints 100% funcionales**

## Notas Importantes

1. **Todos los YAML son 100% funcionales** - no hay duplicados
2. **Seguir orden de ejecución** para pruebas completas
3. **Configurar SMTP** para 2FA completo
4. **Usar variables consistentemente** en el environment
5. **Limpiar datos** entre pruebas si es necesario

## Mantenimiento

- **Actualizar schemas** cuando cambie el backend
- **Añadir nuevos endpoints** cuando se implementen
- **Mantener validaciones** actualizadas con responses
- **Documentar cambios** en este README
