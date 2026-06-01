# REGISTRO CONSOLIDADO DE HALLAZGOS QA

## Proyecto SIGI-E

### LANDING PAGE Y EXPERIENCIA DE USUARIO

1. Inconsistencia visual en alineación y distribución de elementos.
2. Bajo contraste entre textos y fondos en algunas tarjetas.
3. Amplias áreas vacías en dashboard principal.
4. Textos secundarios con legibilidad reducida.
5. Menú desplegable excesivamente grande en algunas resoluciones.
6. Falta agrupación jerárquica de opciones en el menú.
7. No existe separación clara entre operaciones del negocio y opciones de perfil.
8. Pantalla "Acceso Negocio" aporta poca utilidad funcional.
9. Inconsistencia en formato de nombres de usuario entre vistas.


### AUTENTICACIÓN Y MFA

10. Campo de ingreso de código 2FA demasiado amplio para códigos cortos.
11. No existe contador de expiración visible del código MFA.
12. No existe opción visible para reenviar código MFA.
13. Configuración MFA aparentemente redundante respecto al flujo actual de autenticación.

### NEGOCIOS

14. Pantalla de validación de negocio sin funcionalidad administrativa relevante.
15. Necesidad de incorporar geolocalización y ubicación física del negocio.
16. Ausencia de mapa integrado para visualización de negocios cercanos.
17. Restricción de un negocio por usuario validada correctamente (caso exitoso).

### EMPLEADOS

18. Horarios mostrados como identificadores numéricos (1,2,3...) en lugar de días.
19. Representación visual poco intuitiva de los horarios asignados.
20. Falta validación visible de correos duplicados.
21. Falta validación visible de documentos duplicados.
22. Posibles inconsistencias al eliminar empleados con citas asociadas.

### HORARIOS

23. Horarios configurados en negocio no siempre restringen correctamente el agendamiento.
24. Usuarios pueden seleccionar horarios fuera del rango laboral configurado.
25. Selector horario poco intuitivo.
26. Mezcla formatos AM/PM sin claridad suficiente.
27. Posible inconsistencia entre horarios almacenados y horarios mostrados.

### CITAS

28. Permite registrar citas fuera del horario laboral.
29. Posible doble reserva del mismo horario.
30. Cita cancelada puede volver a cancelarse.
31. No existe opción para reprogramar citas.
32. Carrito bloquea reservas indicando servicios de otros negocios sin evidencia visible.
33. Persistencia inconsistente del estado del carrito.
34. Posible conflicto entre localStorage y backend.
35. No existe historial administrativo completo de cambios sobre citas.
36. Falta auditoría de modificaciones.

### CALIFICACIONES Y RANKING

37. Historial muestra "Cita #X" en lugar del negocio calificado.
38. Numeración de citas inconsistente con el historial visible.
39. Falta información descriptiva del servicio calificado.
40. Ranking inicial poco intuitivo.
41. Falta diferenciación clara entre:

    * Tus calificaciones
    * Calificar
    * Ranking
42. Falta tabla dinámica para ranking.
43. Falta actualización automática de posiciones.
44. Falta visualización de promedio global.

### SERVICIOS

45. Servicios duplicados permitidos.
46. Edición de servicios no funcional.
47. Eliminación de servicios inconsistente.
48. El servicio continúa apareciendo tras eliminarlo.
49. Solo es editable el precio.
50. Uso de prompt nativo del navegador.
51. No existe edición completa.
52. No existe activación/desactivación de servicios.
53. Se permiten nombres extremadamente largos.
54. Se permiten descripciones extremadamente largas.
55. Se permiten precios extremadamente altos.
56. Se permiten duraciones extremadamente altas.
57. Error de conexión Frontend-Backend al crear servicios.
58. Falta validación avanzada de datos.

### PRODUCTOS

59. Stock extremadamente alto permitido.
60. No existe validación superior de stock.
61. No existe eliminación visible de productos.
62. Productos inactivos continúan mostrando "Desactivar".
63. No existe opción visible de reactivación.
64. Solo se puede modificar precio.
65. No se puede editar completamente un producto.
66. Falta edición de stock.
67. Falta edición de imagen.
68. Falta edición de nombre.
69. Falta edición de descripción.
70. Botones administrativos sin jerarquía visual.
71. URL de imagen almacenada pero no renderizada.
72. Falta imagen por defecto.

### INVENTARIO

73. No existe historial de movimientos visible.
74. No existe auditoría de entradas y salidas.
75. No existe trazabilidad de responsables.
76. No existen filtros de movimientos.
77. No existe reporte histórico exportable.

### PAGOS Y FACTURACIÓN

78. No existe validación real de transferencias.
79. El sistema no verifica comprobantes de pago.
80. No existe integración con pasarela de pagos.
81. No existe validación automática de pagos.
82. No existe trazabilidad financiera completa.
83. Facturación electrónica pendiente.
84. No existe confirmación de entrega de productos.
85. No existe seguimiento de pedidos.
86. No existe control de dirección de entrega.
87. Flujo de compra incompleto para productos físicos.

### IMÁGENES Y MULTIMEDIA

88. URLs de imágenes no renderizadas en vista usuario.
89. Falta imagen por defecto para servicios.
90. Falta imagen por defecto para empleados.
91. Falta imagen por defecto para productos.
92. Posibles enlaces rotos no controlados.

### ROLES Y SEGURIDAD

93. Validar acceso directo a páginas mediante URL.
94. Verificar protección real de rutas administrativas.
95. Revisar validación backend de roles.
96. Revisar protección JWT.
97. Verificar acceso cruzado entre negocios.
98. Verificar modificación de recursos ajenos.
99. Revisar persistencia de sesiones.

### AWS Y DESPLIEGUE

100. Compatibilidad Linux/Windows pendiente de validación completa.
101. Dockerfile debe revisarse para despliegue final.
102. docker-compose debe validarse en AWS.
103. Variables de entorno deben centralizarse.
104. Migraciones PostgreSQL deben verificarse.
105. Validar ejecución automática de Alembic.
106. Revisar healthchecks.
107. Verificar recuperación ante fallos.
108. Verificar logs de producción.
109. Validar configuración de CORS.
110. Verificar configuración SMTP.

### FUNCIONALIDADES PENDIENTES

111. Ranking público de negocios.
112. Estadísticas administrativas.
113. Carrito de compras completo.
114. Gestión avanzada de inventario.
115. Reportes administrativos.
