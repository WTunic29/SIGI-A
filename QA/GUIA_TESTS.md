# 🧪 Guía Práctica para Ejecutar Tests - SIGI-A (QA)

Los tests automatizados viven en **`QA/tests`**. Ejecutarlos desde **`QA/`** (no dentro de `backend/`), usando `QA/pytest.ini` para cargar la app desde `../backend/app`.

Esta guía te permitirá ejecutar esos tests paso a paso.

---

## ⚡ **Atajo: `qa check` (recomendado)**

Desde `QA/` (PowerShell):

```powershell
pip install -r ..\backend\requirements.txt -r requirements-ci.txt
.\qa.ps1 check
```

Eso ejecuta: validación Postman YAML → presupuesto de `xfail` → **pytest** completo.

Newman (API levantada, sin tocar backend):

```powershell
.\qa.ps1 install    # pnpm install
.\qa.ps1 smoke      # health + OpenAPI vía Newman
```

Node usa **pnpm**, no npm (`QA/package.json`).

---

## 🚀 **Paso 1: Preparar Entorno**

### **1.1 Raíz del repositorio y (opcional) entorno virtual**
```powershell
# Sustituir por la ruta real de tu clon del repo SIGI-A
cd C:\ruta\a\SIGI-A

# Opcional: activar venv si lo tienes en la raíz o en backend
# .\venv\Scripts\activate
```

### **1.2 Dependencias (backend + CI de QA)**
```powershell
pip install -r backend\requirements.txt -r QA\requirements-ci.txt

# Verificar instalación
pytest --version
```

---

## 🧪 **Paso 2: Ejecutar Tests Independientes (Sin Base de Datos)**

### **2.1 Tests de Schemas (Más Rápido)**

Desde **`QA`**:
```powershell
cd QA

# Método 1: Ejecutar archivo standalone
python tests\test_schemas_standalone.py

# Método 2: Con pytest (recomendado)
python -m pytest tests/test_schemas_standalone.py -v
```

**¿Qué debería ver?**
```
=== Testing Schemas con Validaciones Completas ===
✅ UsuarioCreate válido: OK
✅ UsuarioCreate email inválido: Validación correcta
✅ ProductoCreate válido: OK
ℹ️  ProductoCreate precio negativo: Schema no valida (esperado)
ℹ️  ProductoCreate stock negativo: Schema no valida (esperado)
✅ ProductoCreate incompleto: Validación correcta
✅ NegocioCreate válido: OK
✅ NegocioCreate email inválido: Validación correcta
✅ UsuarioCreate rol por defecto: OK
=== Schema Tests Completados: 9/9 tests pasaron ===
🎉 ¡Todos los tests de schemas funcionan correctamente!
```

---

## 🔧 **Paso 3: Si Los Tests Fallan, Solución Rápida**

### **3.1 Ejecutar Tests Manualmente**
```bash
# Copiar y pegar este comando directamente en PowerShell
python -c "
import sys
sys.path.append('.')
from app.schemas.user import UsuarioCreate, UsuarioLogin
from app.schemas.negocio import NegocioCreate
from app.schemas.producto import ProductoCreate
from decimal import Decimal
from pydantic import ValidationError

print('=== Testing Schemas ===')

# Test 1: Usuario válido
try:
    user = UsuarioCreate(
        nombre='Juan',
        apellido='Pérez',
        correo='juan@test.com',
        telefono='555-1234',
        password='password123',
        rol='cliente'
    )
    print('✅ UsuarioCreate: OK')
except Exception as e:
    print(f'❌ UsuarioCreate: {e}')

# Test 2: Email inválido
try:
    UsuarioCreate(
        nombre='Juan',
        apellido='Pérez',
        correo='email_invalido',
        telefono='555-1234',
        password='password123'
    )
    print('❌ Email inválido: Debería fallar')
except ValidationError:
    print('✅ Email inválido: Validación correcta')

# Test 3: Producto válido
try:
    producto = ProductoCreate(
        id_negocio=1,
        nombre='Café Premium',
        precio=Decimal('15000.00'),
        stock=10
    )
    print('✅ ProductoCreate: OK')
except Exception as e:
    print(f'❌ ProductoCreate: {e}')

print('=== Tests Completados ===')
"
```

---

## 📊 **Paso 4: Ejecutar Tests Completos (Avanzado)**

### **4.1 Si Quieres Probar Todos los Tests**

Desde **`QA`** (`pytest.ini` incluye ya `pythonpath = ../backend` y SQLite en memoria en `conftest.py`):
```powershell
cd QA
python -m pytest tests -v --tb=short

# Opcional: cobertura (reporte HTML en QA\htmlcov\)
python -m pytest tests -v --cov=app --cov-report=html
```

Opcional (`conftest_minimal.py` en `QA/tests` solo si lo necesitas para diagnóstico):
```powershell
python tests/conftest_minimal.py
```

### **4.2 Tests por Categoría**
```powershell
cd QA
python -m pytest tests/test_schemas/ -v
python -m pytest tests/test_models/ -v
python -m pytest tests/test_routes/ -v
```

---

## 🔍 **Paso 5: Verificar Resultados**

### **5.1 Resultados Esperados**
- **Schemas**: 9/9 tests deben pasar
- **Models**: Pueden fallar por configuración de base de datos
- **Routes**: Pueden fallar por configuración de autenticación

### **5.2 Si Algo Falla**
```powershell
cd QA

python -m pytest tests/test_schemas_standalone.py -v -s --tb=long
```

---

## 🛠️ **Paso 6: Solución de Problemas Comunes**

### **Problema 1: "No module named 'pytest'"**
```powershell
pip install -r backend\requirements.txt -r QA\requirements-ci.txt
```

### **Problema 2: "ImportError while loading conftest"**
```bash
# Usar el archivo standalone en su lugar
python tests/test_schemas_standalone.py
```

### **Problema 3: "OperationalError: unknown database core"**
```bash
# Esto es normal, usar tests standalone
python tests/test_schemas_standalone.py
```

### **Problema 4: "ValidationError"**
```bash
# Esto es bueno, significa que las validaciones funcionan
# Los tests están detectando errores correctamente
```

---

## 📈 **Paso 7: Generar Reporte (Opcional)**

### **7.1 Si Pytest Funciona**
```powershell
cd QA
python -m pytest tests -v --cov=app --cov-report=html
# Informe HTML: QA\htmlcov\index.html
```

---

## 🎯 **Resumen de Comandos Clave**

### **Para Empezar (Recomendado)**
```powershell
cd C:\ruta\a\SIGI-A\QA
python tests\test_schemas_standalone.py
```

### **Para Testing Completo**
```powershell
cd C:\ruta\a\SIGI-A\QA
python -m pytest tests -v --tb=short
```

### **Para Debug**
```powershell
cd C:\ruta\a\SIGI-A\QA
python -m pytest tests/test_schemas/ -v -s --tb=long
```

---

## ✅ **Checklist de Verificación**

- [ ] Entorno virtual activado
- [ ] Dependencias instaladas
- [ ] Tests de schemas ejecutados
- [ ] 9/9 tests de schemas pasan
- [ ] Entendido el significado de los resultados
- [ ] Si falla, identificado el problema específico

---

## 🔎 Postman (lint del workspace YAML)

Desde **`QA`**:

```powershell
python scripts\validate_postman_workspace.py
```

Comprueba que cada request tenga `method` / `url` / `order`, que no haya `order` duplicados y que los placeholders `{{variable}}` estén declarados en los entornos o en `postman/collections/SIGI-A/.resources/definition.yaml`. Más detalle en **`QA/postman/README.md`**.

---

## 🚨 **Qué Hacer Si Todo Falla**

### **Opción Ultra-Simple**
```bash
# Solo verificar que los schemas importen correctamente
python -c "
from app.schemas.user import UsuarioCreate
from app.schemas.negocio import NegocioCreate
from app.schemas.producto import ProductoCreate
print('✅ Todos los schemas importan correctamente')
"
```

### **Opción Manual**
```bash
# Crear usuario de prueba manualmente
python -c "
from app.schemas.user import UsuarioCreate
user = UsuarioCreate(
    nombre='Carlos',
    apellido='Barbero',
    correo='carlos@barberia.com',
    telefono='555-1234',
    password='password123',
    rol='negocio'
)
print(f'✅ Usuario creado: {user.nombre} - Rol: {user.rol}')
"
```

---

**Con esta guía podrás ejecutar los tests del backend SIGI-A de manera independiente y verificar su funcionamiento.** 🧪
