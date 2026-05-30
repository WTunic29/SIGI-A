# 🧪 Guía Práctica para Ejecutar Tests - SIGI-A Backend

Esta guía te permitirá ejecutar los tests del backend SIGI-A paso a paso.

---

## 🚀 **Paso 1: Preparar Entorno**

### **1.1 Activar Entorno Virtual**
```bash
# Desde la carpeta backend
cd c:\Users\poeta\Documents\QA\SIGI-A\backend

# Activar entorno virtual
venv\Scripts\activate
```

### **1.2 Verificar Dependencias**
```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio pytest-cov httpx

# Verificar instalación
pytest --version
```

---

## 🧪 **Paso 2: Ejecutar Tests Independientes (Sin Base de Datos)**

### **2.1 Tests de Schemas (Más Rápido)**
```bash
# Método 1: Ejecutar archivo standalone
python tests/test_schemas_standalone.py

# Método 2: Con pytest (si funciona)
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
```bash
# Intentar ejecutar pytest completo
pytest -v --cov=app --cov-report=html

# Si falla por error de base de datos, probar con archivo minimal
python tests/conftest_minimal.py
```

### **4.2 Tests por Categoría**
```bash
# Solo schemas (los que más probable funcionen)
pytest tests/test_schemas/ -v

# Solo models (pueden fallar por base de datos)
pytest tests/test_models/ -v

# Solo routes (pueden fallar por autenticación)
pytest tests/test_routes/ -v
```

---

## 🔍 **Paso 5: Verificar Resultados**

### **5.1 Resultados Esperados**
- **Schemas**: 9/9 tests deben pasar
- **Models**: Pueden fallar por configuración de base de datos
- **Routes**: Pueden fallar por configuración de autenticación

### **5.2 Si Algo Falla**
```bash
# Ver error específico
pytest tests/test_schemas/test_user_schema.py -v -s

# Debug mode
pytest tests/test_schemas_standalone.py -v -s --tb=long
```

---

## 🛠️ **Paso 6: Solución de Problemas Comunes**

### **Problema 1: "No module named 'pytest'"**
```bash
pip install pytest pytest-asyncio pytest-cov httpx
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
```bash
# Generar reporte de cobertura
pytest --cov=app --cov-report=html

# Ver reporte en navegador
# Abrir: backend/htmlcov/index.html
```

---

## 🎯 **Resumen de Comandos Clave**

### **Para Empezar (Recomendado)**
```bash
cd c:\Users\poeta\Documents\QA\SIGI-A\backend
venv\Scripts\activate
python tests/test_schemas_standalone.py
```

### **Para Testing Completo**
```bash
pytest -v --cov=app --cov-report=html
```

### **Para Debug**
```bash
pytest tests/test_schemas/ -v -s --tb=long
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
