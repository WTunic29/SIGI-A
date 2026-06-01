# INFORME DE HALLAZGOS QA Y OBSERVACIONES FUNCIONALES

## Proyecto SIGI-E

### Revisión Funcional – Módulos de Negocio, Inventario, Citas y Servicios

**Fecha:** Mayo 2026
**Responsable:** Christian López
**Rol:** QA / Documentación

---

# Hallazgo 1 – Restricción incorrecta al agendar citas

### Módulo

Agendamiento de citas

### Descripción

Al intentar registrar una cita, el sistema muestra el mensaje:

> "No puedes mezclar servicios de diferentes negocios en el mismo carrito"

aunque aparentemente no existen servicios agregados en el carrito actual.

### Comportamiento esperado

El sistema debe permitir registrar la cita si el carrito está vacío o mostrar claramente qué elemento genera el conflicto.

### Impacto

Puede impedir la creación de citas válidas y generar confusión al usuario.

### Clasificación

Error funcional

### Prioridad

Alta

---

# Hallazgo 2 – Servicios duplicados

### Módulo

Gestión de Servicios

### Descripción

El sistema permite registrar múltiples servicios con el mismo nombre, precio y duración.

### Comportamiento esperado

El sistema debería validar duplicados o advertir al administrador antes de crear registros idénticos.

### Impacto

Duplicidad de información y posibles inconsistencias en reportes y reservas.

### Clasificación

Error de validación

### Prioridad

Media

---

# Hallazgo 3 – Edición de servicios no funcional

### Módulo

Gestión de Servicios

### Descripción

El botón "Editar" no refleja cambios visibles o no persiste correctamente la información modificada.

### Comportamiento esperado

Los cambios realizados deben almacenarse y visualizarse inmediatamente.

### Clasificación

Error funcional

### Prioridad

Alta

---

# Hallazgo 4 – Eliminación de servicios inconsistente

### Módulo

Gestión de Servicios

### Descripción

Después de eliminar un servicio, este continúa apareciendo en el listado.

### Comportamiento esperado

El servicio debe desaparecer del listado o reflejar claramente un estado inactivo.

### Clasificación

Error funcional

### Prioridad

Alta

---

# Hallazgo 5 – Valores extremos en servicios

### Módulo

Gestión de Servicios

### Descripción

El sistema permite registrar:

* Duraciones extremadamente altas.
* Precios extremadamente elevados.
* Nombres excesivamente largos.
* Descripciones extensas.

### Comportamiento esperado

Deben existir límites de negocio para evitar datos irreales.

### Clasificación

Observación de validación

### Prioridad

Media

---

# Hallazgo 6 – Error de comunicación Frontend-Backend

### Módulo

Gestión de Servicios

### Descripción

Durante la creación de servicios se presenta el mensaje:

> "No se pudo conectar con el backend. Verifica que el servicio de Render esté activo y que la ruta exista en Swagger."

### Comportamiento esperado

La creación debe completarse correctamente o mostrar un mensaje más específico.

### Clasificación

Error de integración

### Prioridad

Crítica

---

# Hallazgo 7 – Configuración MFA redundante

### Módulo

Perfil de Usuario

### Descripción

Existe una opción para activar autenticación adicional mediante aplicaciones autenticadoras.

Sin embargo, durante el inicio de sesión el sistema ya solicita el proceso de autenticación mediante QR.

### Comportamiento esperado

Definir claramente si MFA es obligatorio u opcional para evitar duplicidad de flujos.

### Clasificación

Observación funcional

### Prioridad

Baja

---

# Hallazgo 8 – Stock sin límites de validación

### Módulo

Inventario

### Descripción

El sistema permite ingresar cantidades extremadamente altas para el stock de productos.

### Comportamiento esperado

Validar cantidades máximas razonables según reglas de negocio.

### Clasificación

Observación de validación

### Prioridad

Media

---

# Hallazgo 9 – Falta historial de movimientos

### Módulo

Inventario

### Descripción

Se permite registrar movimientos de inventario, pero no existe una vista para consultar el historial completo.

### Comportamiento esperado

El administrador debe poder consultar entradas, salidas, ajustes y responsables.

### Clasificación

Mejora funcional

### Prioridad

Media

---

# Hallazgo 10 – Pantalla de acceso con poco valor funcional

### Módulo

Permisos

### Descripción

La pantalla "Acceso Negocio" muestra únicamente el estado validado y datos básicos.

### Comportamiento esperado

Redireccionar automáticamente o proporcionar información administrativa útil.

### Clasificación

Observación de experiencia de usuario

### Prioridad

Baja

---

# Hallazgo 11 – Representación incorrecta de horarios

### Módulo

Gestión de Empleados

### Descripción

Los horarios se visualizan utilizando identificadores numéricos:

* 1
* 2
* 3

en lugar de los nombres de los días.

### Comportamiento esperado

Mostrar:

* Lunes
* Martes
* Miércoles
* Jueves
* Viernes
* Sábado
* Domingo

### Clasificación

Error de presentación

### Prioridad

Media

---

# Hallazgo 12 – Cancelación repetida de citas

### Módulo

Gestión de Citas

### Descripción

Las citas canceladas continúan mostrando la opción "Cancelar".

### Comportamiento esperado

Una cita cancelada no debería permitir nuevas cancelaciones.

### Clasificación

Error funcional

### Prioridad

Alta

---

# Hallazgo 13 – Falta de reprogramación de citas

### Módulo

Gestión de Citas

### Descripción

No existe una opción para modificar fecha u horario de una cita ya creada.

### Comportamiento esperado

Permitir reprogramación o edición controlada de citas.

### Clasificación

Mejora funcional

### Prioridad

Media

---

# Hallazgo 14 – Restricción correcta de negocios por usuario

### Módulo

Registro de Negocio

### Descripción

El sistema impide correctamente que un mismo usuario registre múltiples negocios.

### Resultado

Comportamiento validado satisfactoriamente.

### Clasificación

Caso de prueba exitoso

### Prioridad

N/A

---

# Conclusión General

Durante la ejecución de pruebas funcionales se identificaron errores relacionados con:

* Gestión de servicios.
* Integración Frontend-Backend.
* Inventario.
* Gestión de citas.
* Representación de horarios.
* Validaciones de negocio.

Adicionalmente se detectaron oportunidades de mejora en experiencia de usuario, auditoría de inventario y administración de citas.

Se recomienda priorizar la corrección de los hallazgos clasificados como **Críticos y Altos** antes del despliegue definitivo en AWS y antes de la sustentación del proyecto.
