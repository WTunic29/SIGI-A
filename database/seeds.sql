-- SIGI-A - Seeds corregidos
-- Usuarios de prueba:
--   admin@sigi-a.com    / Admin123*
--   negocio@sigi-a.com  / Admin123*
--   cliente@sigi-a.com  / Admin123*

BEGIN;

INSERT INTO core.roles (nombre, descripcion)
VALUES
    ('admin', 'Administrador del sistema'),
    ('superadmin', 'Superusuario con permisos globales'),
    ('negocio', 'Propietario o administrador de negocio'),
    ('cliente', 'Usuario cliente final')
ON CONFLICT (nombre) DO UPDATE
SET descripcion = EXCLUDED.descripcion;

INSERT INTO core.usuarios (
    nombre, apellido, correo, telefono, password_hash, estado, rol,
    mfa_totp_enabled, mfa_totp_secret
)
VALUES (
    'Super', 'Admin', 'admin@sigi-a.com', '3000000000',
    '$2y$12$qwCh3EzIypPXE7uQNNis2eOIPefNVnw/teYQTgEIgFTz4VOs/0nOS', 'activo', 'admin',
    false, NULL
)
ON CONFLICT (correo) DO UPDATE
SET nombre = EXCLUDED.nombre,
    apellido = EXCLUDED.apellido,
    telefono = EXCLUDED.telefono,
    password_hash = EXCLUDED.password_hash,
    estado = EXCLUDED.estado,
    rol = EXCLUDED.rol,
    mfa_totp_enabled = EXCLUDED.mfa_totp_enabled,
    mfa_totp_secret = EXCLUDED.mfa_totp_secret;

INSERT INTO core.usuarios (
    nombre, apellido, correo, telefono, password_hash, estado, rol,
    mfa_totp_enabled, mfa_totp_secret
)
VALUES (
    'Negocio', 'Demo', 'negocio@sigi-a.com', '3001111111',
    '$2y$12$qwCh3EzIypPXE7uQNNis2eOIPefNVnw/teYQTgEIgFTz4VOs/0nOS', 'activo', 'negocio',
    false, NULL
)
ON CONFLICT (correo) DO UPDATE
SET nombre = EXCLUDED.nombre,
    apellido = EXCLUDED.apellido,
    telefono = EXCLUDED.telefono,
    password_hash = EXCLUDED.password_hash,
    estado = EXCLUDED.estado,
    rol = EXCLUDED.rol,
    mfa_totp_enabled = EXCLUDED.mfa_totp_enabled,
    mfa_totp_secret = EXCLUDED.mfa_totp_secret;

INSERT INTO core.usuarios (
    nombre, apellido, correo, telefono, password_hash, estado, rol,
    mfa_totp_enabled, mfa_totp_secret
)
VALUES (
    'Cliente', 'Demo', 'cliente@sigi-a.com', '3002222222',
    '$2y$12$qwCh3EzIypPXE7uQNNis2eOIPefNVnw/teYQTgEIgFTz4VOs/0nOS', 'activo', 'cliente',
    false, NULL
)
ON CONFLICT (correo) DO UPDATE
SET nombre = EXCLUDED.nombre,
    apellido = EXCLUDED.apellido,
    telefono = EXCLUDED.telefono,
    password_hash = EXCLUDED.password_hash,
    estado = EXCLUDED.estado,
    rol = EXCLUDED.rol,
    mfa_totp_enabled = EXCLUDED.mfa_totp_enabled,
    mfa_totp_secret = EXCLUDED.mfa_totp_secret;

INSERT INTO core.usuario_rol (id_usuario, id_rol)
SELECT u.id_usuario, r.id_rol
FROM core.usuarios u
JOIN core.roles r ON r.nombre = u.rol
WHERE u.correo IN ('admin@sigi-a.com', 'negocio@sigi-a.com', 'cliente@sigi-a.com')
ON CONFLICT (id_usuario, id_rol) DO NOTHING;

INSERT INTO core.categorias_negocio (nombre, descripcion)
SELECT 'Barbería', 'Servicios de barbería, estética y cuidado personal'
WHERE NOT EXISTS (
    SELECT 1 FROM core.categorias_negocio WHERE nombre = 'Barbería'
);

INSERT INTO core.negocios (
    id_usuario_propietario,
    nombre_negocio,
    descripcion,
    direccion,
    ciudad,
    telefono,
    email_negocio,
    color_primario,
    color_secundario,
    categoria_principal,
    estado
)
SELECT
    u.id_usuario,
    'Barbería Demo SIGI-A',
    'Negocio de prueba para validar productos, servicios, empleados y citas.',
    'Calle 123 #45-67',
    'Bogotá',
    '3001111111',
    'negocio@sigi-a.com',
    '#D6B84F',
    '#111111',
    'Barbería',
    'activo'
FROM core.usuarios u
WHERE u.correo = 'negocio@sigi-a.com'
AND NOT EXISTS (
    SELECT 1 FROM core.negocios n WHERE n.email_negocio = 'negocio@sigi-a.com'
);

INSERT INTO core.productos (
    id_negocio, nombre, descripcion, precio, stock, imagen_url, estado
)
SELECT
    n.id_negocio,
    'Cera para cabello',
    'Producto de prueba para tienda.',
    25000,
    20,
    NULL,
    'activo'
FROM core.negocios n
WHERE n.email_negocio = 'negocio@sigi-a.com'
AND NOT EXISTS (
    SELECT 1 FROM core.productos p
    WHERE p.id_negocio = n.id_negocio
    AND p.nombre = 'Cera para cabello'
);

INSERT INTO core.servicios (
    id_negocio, nombre, descripcion, duracion_minutos, precio, estado, imagen_url
)
SELECT
    n.id_negocio,
    'Corte de cabello',
    'Servicio de prueba para disponibilidad y citas.',
    40,
    30000,
    'activo',
    NULL
FROM core.negocios n
WHERE n.email_negocio = 'negocio@sigi-a.com'
AND NOT EXISTS (
    SELECT 1 FROM core.servicios s
    WHERE s.id_negocio = n.id_negocio
    AND s.nombre = 'Corte de cabello'
);

INSERT INTO core.empleados (
    id_negocio, nombre, apellido, telefono, email, especialidad, foto_url, estado
)
SELECT
    n.id_negocio,
    'Carlos',
    'Barbero',
    '3003333333',
    'empleado@sigi-a.com',
    'Cortes clásicos y modernos',
    NULL,
    'activo'
FROM core.negocios n
WHERE n.email_negocio = 'negocio@sigi-a.com'
AND NOT EXISTS (
    SELECT 1 FROM core.empleados e
    WHERE e.id_negocio = n.id_negocio
    AND e.email = 'empleado@sigi-a.com'
);

INSERT INTO core.empleado_servicio (id_empleado, id_servicio)
SELECT e.id_empleado, s.id_servicio
FROM core.empleados e
JOIN core.negocios n ON n.id_negocio = e.id_negocio
JOIN core.servicios s ON s.id_negocio = n.id_negocio
WHERE e.email = 'empleado@sigi-a.com'
AND s.nombre = 'Corte de cabello'
ON CONFLICT (id_empleado, id_servicio) DO NOTHING;

INSERT INTO core.horarios_empleado (
    id_empleado, dia_semana, hora_inicio, hora_fin, disponible
)
SELECT
    e.id_empleado,
    d.dia,
    TIME '09:00',
    TIME '18:00',
    true
FROM core.empleados e
CROSS JOIN generate_series(1, 7) AS d(dia)
WHERE e.email = 'empleado@sigi-a.com'
AND NOT EXISTS (
    SELECT 1 FROM core.horarios_empleado h
    WHERE h.id_empleado = e.id_empleado
    AND h.dia_semana = d.dia
);

COMMIT;
