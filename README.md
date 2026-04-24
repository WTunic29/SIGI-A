# SIGI-E

Sistema inteligente de gestión para centros de estética (barberías, peluquerías, tatuajes, centros de belleza,  etc).

---

## Descripción

SIGI-E es una plataforma que permite conectar múltiples negocios de estética en un solo sistema, donde:

### Usuarios pueden:
- Ver negocios cercanos
- Agendar citas
- Calificar servicios
- Comprar servicios/productos

### Negocios pueden:
- Gestionar empleados
- Administrar citas en tiempo real
- Controlar inventario
- Ver reportes y métricas

---

## Backend (en desarrollo)

Tecnologías:
- Python (FastAPI o Flask)
- PostgreSQL
- SQLAlchemy
- JWT (autenticación)

---

## Base de datos

La base de datos está diseñada en PostgreSQL con las siguientes entidades principales:

- usuarios
- negocios
- empleados
- servicios
- citas

Relaciones:
- Un usuario puede tener un negocio
- Un negocio tiene empleados y servicios
- Un usuario puede agendar citas con empleados

---

## Estructura del proyecto
