# 📊 SIGI-A - Módulo de Calificaciones v2.0

## Descripción General

La versión 2.0 del módulo de calificaciones incorpora nuevas funcionalidades orientadas a mejorar la experiencia de usuario, facilitar el proceso de evaluación de servicios y proporcionar métricas de reputación para los negocios registrados en la plataforma.

---

# 📁 Archivos Modificados

## Backend

```txt
backend/app/routes/calificacion.py
backend/app/schemas/calificacion.py
```

## Frontend

```txt
frontend/usuario.html
frontend/js/main.js
frontend/css/styles.css
```

## Backend relacionado (sin cambios estructurales)

```txt
backend/app/models/calificacion.py
backend/app/main.py
```

---

# ⭐ Ranking de Negocios

## Funcionalidad

Se implementó un sistema de clasificación de negocios basado en las evaluaciones realizadas por los usuarios.

### Endpoint

```http
GET /calificaciones/ranking/all
```

### Información Retornada

* Posición dentro del ranking.
* ID del negocio.
* Nombre del negocio.
* Promedio de calificación.
* Total de opiniones recibidas.

### Lógica Implementada

* Agrupación de calificaciones por negocio.
* Cálculo de promedio mediante `AVG()`.
* Conteo de opiniones mediante `COUNT()`.
* Ordenamiento descendente por puntuación.
* Asignación automática de posiciones.

### Schema Agregado

```txt
RankingNegocio
```

#### Campos

```txt
posicion
id_negocio
nombre_negocio
promedio
total_calificaciones
```

### Integración Frontend

* Consumo de `GET /calificaciones/ranking/all`.
* Visualización mediante tarjetas.
* Visualización mediante tabla dinámica.
* Búsqueda por nombre de negocio.
* Ordenamiento por promedio.
* Ordenamiento por cantidad de opiniones.
* Actualización automática después de crear o eliminar una calificación.

### Funciones Frontend

```javascript
cargarRankingTab()
renderizarRanking()
renderizarRankingTabla()
filtrarRanking()
aplicarOrdenamientoRanking()
```

### Contenedores Frontend

```txt
#tab-ranking
#listaRankingTab
#tablaRankingBody
#rankingMsg
#buscarRanking
#ordenamientoRanking
```

---

# 📝 Calificar Servicios

## Funcionalidad

Se implementó la consulta de citas finalizadas que aún no han sido calificadas.

### Endpoint

```http
GET /calificaciones/citas-pendientes/all
```

### Información Retornada

* ID de la cita.
* Negocio asociado.
* Empleado responsable.
* Servicio realizado.
* Fecha de atención.
* Horario de atención.

### Objetivo

Permitir que el usuario visualice únicamente los servicios pendientes de evaluación.

### Schema Agregado

```txt
CitaPendienteCalificacion
```

#### Campos

```txt
id_cita
id_negocio
id_empleado
negocio_nombre
empleado_nombre
empleado_apellido
servicio_nombre
servicio_id
fecha
hora_inicio
hora_fin
```

### Integración Frontend

* Consumo de `GET /calificaciones/citas-pendientes/all`.
* Listado de citas pendientes.
* Apertura de formulario de calificación.
* Registro mediante `POST /calificaciones/`.
* Actualización automática de:

  * Citas pendientes.
  * Mis calificaciones.
  * Ranking.

### Funciones Frontend

```javascript
cargarCitasPendientesTab()
abrirFormularioCalificacion()
calificarCita()
```

### Contenedores Frontend

```txt
#tab-calificar
#listaCitasPendientesTab
#calificarMsg
```

---

# 📋 Gestión de Calificaciones

## Funcionalidades

El módulo conserva todas las operaciones CRUD existentes.

### Endpoints

```http
POST   /calificaciones/
GET    /calificaciones/
GET    /calificaciones/{id}
PUT    /calificaciones/{id}
DELETE /calificaciones/{id}
```

### Integración Frontend

* Consulta del historial de calificaciones.
* Eliminación de calificaciones.
* Actualización automática del ranking.
* Actualización automática del dashboard.

### Funciones Frontend

```javascript
cargarMisCalificacionesTab()
eliminarCalificacion()
```

### Contenedores Frontend

```txt
#tab-mis-calificaciones
#listaMisCalificacionesTab
#misCalsMsg
```

---

# 📈 Dashboard Estadístico

## Archivo

```txt
frontend/usuario.html
```

### Indicadores

```txt
#statMisCalificaciones
#statPromedioPersonal
#statPendientesCalificar
#statMejorNegocio
```

### Función

```javascript
actualizarDashboardCalificaciones()
```

### Métricas Mostradas

* Total de opiniones realizadas por el usuario.
* Promedio personal de puntuaciones.
* Cantidad de citas pendientes por calificar.
* Mejor negocio según ranking actual.

---

# 🎨 Estilos Frontend

## Archivo

```txt
frontend/css/styles.css
```

### Clases Agregadas

```txt
.rating-stats-dashboard
.rating-stats-dashboard article
.rating-stats-dashboard span
.rating-stats-dashboard strong
.rating-stars.compact
.ranking-table-wrap
.ranking-table
.ranking-table th
.ranking-table td
```

### Responsive

```css
@media (max-width: 768px)
@media (max-width: 480px)
```

### Objetivo

* Estilizar dashboard estadístico.
* Estilizar ranking.
* Estilizar tabla dinámica.
* Mantener compatibilidad móvil y escritorio.

---

# 🔄 Flujo Funcional

```txt
Usuario
   │
   ├── Consulta citas pendientes
   │
   ▼
Selecciona servicio pendiente
   │
   ▼
Registra calificación
   │
   ▼
Se almacena en PostgreSQL
   │
   ▼
Actualiza promedio del negocio
   │
   ▼
Actualiza ranking general
   │
   ▼
Frontend refresca:
   - citas pendientes
   - mis calificaciones
   - dashboard estadístico
   - ranking
```

---

# 📌 Resumen de Cambios

| Área           | Implementación                                  |
| -------------- | ----------------------------------------------- |
| Ranking        | Endpoint `/calificaciones/ranking/all`          |
| Ranking        | Schema `RankingNegocio`                         |
| Ranking        | Promedio y conteo de opiniones                  |
| Ranking        | Tarjetas visuales                               |
| Ranking        | Tabla dinámica                                  |
| Ranking        | Búsqueda por negocio                            |
| Ranking        | Ordenamiento dinámico                           |
| Calificar      | Endpoint `/calificaciones/citas-pendientes/all` |
| Calificar      | Schema `CitaPendienteCalificacion`              |
| Calificar      | Vista de citas pendientes                       |
| Calificar      | Formulario de registro                          |
| Calificar      | Refresco automático                             |
| Calificaciones | CRUD completo                                   |
| Calificaciones | Historial de usuario                            |
| Calificaciones | Eliminación desde frontend                      |
| Dashboard      | Indicadores estadísticos                        |
| Frontend       | Integración completa en usuario.html            |
| Frontend       | Lógica implementada en main.js                  |
| Frontend       | Estilos implementados en styles.css             |
| Base de Datos  | Sin nuevas tablas                               |
| Base de Datos  | Sin nuevas migraciones                          |
| Modelos        | Reutilización de Calificacion                   |
| QA             | Colecciones Postman actualizadas                |

---

# ✅ Validación

```bash
node --check frontend/js/main.js
```

Resultado:

```txt
OK
```

---

# 🚀 Alcance Final

## Backend

* Ranking de negocios.
* Consulta de citas pendientes.
* CRUD de calificaciones.
* Reutilización de estructura existente.
* Sin nuevas migraciones.

## Frontend

* Pestaña **Mis Calificaciones**.
* Pestaña **Calificar**.
* Pestaña **Ranking**.
* Dashboard estadístico.
* Tabla dinámica.
* Búsqueda y ordenamiento.

## Base de Datos

* Reutilización de la tabla `calificaciones`.
* Sin cambios estructurales.

## DevOps

* No requiere nuevas variables de entorno.
* No requiere nuevas migraciones.
* No requiere cambios de infraestructura.
* Compatible con el despliegue actual.

---

## Estado de Implementación

| Componente               | Estado                          |
| ------------------------ | ------------------------------- |
| Backend Ranking          | ✅ Completado                    |
| Backend Citas Pendientes | ✅ Completado                    |
| Frontend Ranking         | ✅ Completado                    |
| Frontend Calificar       | ✅ Completado                    |
| Dashboard Estadístico    | ✅ Completado                    |
| Tabla Dinámica           | ✅ Completado                    |
| Base de Datos            | ✅ Compatible                    |
| QA Funcional             | ⏳ Pendiente de validación final |
| Despliegue AWS           | ⏳ Pendiente                     |

```

**Versión:** Calificaciones v2.0  
**Proyecto:** SIGI-A
```
