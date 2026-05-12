BEGIN;

CREATE SCHEMA IF NOT EXISTS core;
SET search_path TO core, public;

-- =========================
-- TABLAS BASE DE SEGURIDAD
-- =========================

CREATE TABLE roles (
    id_rol            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre            VARCHAR(50) NOT NULL UNIQUE,
    descripcion       VARCHAR(255)
);

CREATE TABLE usuarios (
    id_usuario        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre            VARCHAR(100) NOT NULL,
    apellido          VARCHAR(100) NOT NULL,
    correo            VARCHAR(150) NOT NULL UNIQUE,
    telefono          VARCHAR(30),
    password_hash     VARCHAR(255) NOT NULL,
    estado            VARCHAR(20) NOT NULL DEFAULT 'activo'
                      CHECK (estado IN ('activo', 'inactivo', 'bloqueado')),
    fecha_creacion    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_login      TIMESTAMP
);

CREATE TABLE usuario_rol (
    id_usuario_rol    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario        BIGINT NOT NULL,
    id_rol            BIGINT NOT NULL,
    UNIQUE (id_usuario, id_rol),
    CONSTRAINT fk_usuario_rol_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_usuario_rol_rol
        FOREIGN KEY (id_rol) REFERENCES roles(id_rol) ON DELETE CASCADE
);

CREATE TABLE sesiones (
    id_sesion         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario        BIGINT NOT NULL,
    token             VARCHAR(500) NOT NULL UNIQUE,
    fecha_inicio      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion  TIMESTAMP NOT NULL,
    ip                VARCHAR(50),
    user_agent        TEXT,
    activa            BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_sesiones_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE tokens_recuperacion (
    id_token          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario        BIGINT NOT NULL,
    token             VARCHAR(255) NOT NULL UNIQUE,
    fecha_creacion    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion  TIMESTAMP NOT NULL,
    usado             BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_tokens_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE verificacion_2fa (
    id_verificacion   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario        BIGINT NOT NULL,
    codigo            VARCHAR(20) NOT NULL,
    metodo            VARCHAR(20) NOT NULL DEFAULT 'email'
                      CHECK (metodo IN ('email', 'sms', 'app')),
    fecha_creacion    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion  TIMESTAMP NOT NULL,
    usado             BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_verificacion_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- =========================
-- NEGOCIOS Y CATEGORÍAS
-- =========================

CREATE TABLE categorias_negocio (
    id_categoria      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre            VARCHAR(80) NOT NULL UNIQUE,
    descripcion       VARCHAR(255)
);

CREATE TABLE negocios (
    id_negocio            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario_propietario BIGINT NOT NULL,
    nombre_negocio        VARCHAR(150) NOT NULL,
    descripcion           TEXT,
    direccion             VARCHAR(255),
    ciudad                VARCHAR(100),
    latitud               NUMERIC(9,6),
    longitud              NUMERIC(9,6),
    telefono              VARCHAR(30),
    email_negocio         VARCHAR(150),
    logo_url              TEXT,
    color_primario        VARCHAR(20),
    color_secundario      VARCHAR(20),
    categoria_principal   VARCHAR(80),
    estado                VARCHAR(20) NOT NULL DEFAULT 'activo'
                          CHECK (estado IN ('activo', 'inactivo', 'suspendido')),
    fecha_creacion        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_negocios_propietario
        FOREIGN KEY (id_usuario_propietario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE negocio_categoria (
    id_negocio_categoria BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_negocio           BIGINT NOT NULL,
    id_categoria         BIGINT NOT NULL,
    UNIQUE (id_negocio, id_categoria),
    CONSTRAINT fk_negocio_categoria_negocio
        FOREIGN KEY (id_negocio) REFERENCES negocios(id_negocio) ON DELETE CASCADE,
    CONSTRAINT fk_negocio_categoria_categoria
        FOREIGN KEY (id_categoria) REFERENCES categorias_negocio(id_categoria) ON DELETE CASCADE
);

CREATE TABLE imagenes_negocio (
    id_imagen          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_negocio         BIGINT NOT NULL,
    url_imagen         TEXT NOT NULL,
    descripcion        VARCHAR(255),
    principal          BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_imagenes_negocio
        FOREIGN KEY (id_negocio) REFERENCES negocios(id_negocio) ON DELETE CASCADE
);

-- =========================
-- EMPLEADOS Y SERVICIOS
-- =========================

CREATE TABLE empleados (
    id_empleado        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_negocio         BIGINT NOT NULL,
    nombre             VARCHAR(100) NOT NULL,
    apellido           VARCHAR(100) NOT NULL,
    telefono           VARCHAR(30),
    email              VARCHAR(150),
    especialidad       VARCHAR(120),
    foto_url           TEXT,
    estado             VARCHAR(20) NOT NULL DEFAULT 'activo'
                      CHECK (estado IN ('activo', 'inactivo')),
    CONSTRAINT fk_empleados_negocio
        FOREIGN KEY (id_negocio) REFERENCES negocios(id_negocio) ON DELETE CASCADE
);

CREATE TABLE servicios (
    id_servicio        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_negocio         BIGINT NOT NULL,
    nombre             VARCHAR(120) NOT NULL,
    descripcion        TEXT,
    duracion_minutos   INTEGER NOT NULL CHECK (duracion_minutos > 0),
    precio             NUMERIC(12,2) NOT NULL CHECK (precio >= 0),
    estado             VARCHAR(20) NOT NULL DEFAULT 'activo'
                      CHECK (estado IN ('activo', 'inactivo')),
    imagen_url         TEXT,
    CONSTRAINT fk_servicios_negocio
        FOREIGN KEY (id_negocio) REFERENCES negocios(id_negocio) ON DELETE CASCADE
);

CREATE TABLE empleado_servicio (
    id_empleado_servicio BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_empleado          BIGINT NOT NULL,
    id_servicio          BIGINT NOT NULL,
    UNIQUE (id_empleado, id_servicio),
    CONSTRAINT fk_empleado_servicio_empleado
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE CASCADE,
    CONSTRAINT fk_empleado_servicio_servicio
        FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio) ON DELETE CASCADE
);

CREATE TABLE horarios_empleado (
    id_horario         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_empleado        BIGINT NOT NULL,
    dia_semana         SMALLINT NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
    hora_inicio        TIME NOT NULL,
    hora_fin           TIME NOT NULL,
    disponible         BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_horario_valido
        CHECK (hora_fin > hora_inicio),
    CONSTRAINT fk_horarios_empleado
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE CASCADE
);

-- =========================
-- CITAS Y CALIFICACIONES
-- =========================

CREATE TABLE citas (
    id_cita            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente         BIGINT NOT NULL,
    id_negocio         BIGINT NOT NULL,
    id_empleado        BIGINT NOT NULL,
    fecha              DATE NOT NULL,
    hora_inicio        TIME NOT NULL,
    hora_fin           TIME NOT NULL,
    estado             VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                      CHECK (estado IN ('pendiente', 'confirmada', 'cancelada', 'completada', 'no_asistio')),
    observaciones      TEXT,
    fecha_creacion     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_cita_horas
        CHECK (hora_fin > hora_inicio),
    CONSTRAINT fk_citas_cliente
        FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_citas_negocio
        FOREIGN KEY (id_negocio) REFERENCES negocios(id_negocio) ON DELETE CASCADE,
    CONSTRAINT fk_citas_empleado
        FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE CASCADE
);

CREATE TABLE detalle_cita (
    id_detalle_cita    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cita            BIGINT NOT NULL,
    id_servicio        BIGINT NOT NULL,
    precio             NUMERIC(12,2) NOT NULL CHECK (precio >= 0),
    duracion           INTEGER NOT NULL CHECK (duracion > 0),
    CONSTRAINT fk_detalle_cita_cita
        FOREIGN KEY (id_cita) REFERENCES citas(id_cita) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_cita_servicio
        FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio)
);

CREATE TABLE calificaciones (
    id_calificacion    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente         BIGINT NOT NULL,
    id_negocio         BIGINT NOT NULL,
    id_cita            BIGINT,
    puntuacion         SMALLINT NOT NULL CHECK (puntuacion BETWEEN 1 AND 5),
    comentario         TEXT,
    fecha              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_calificacion_cliente
        FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_calificacion_negocio
        FOREIGN KEY (id_negocio) REFERENCES negocios(id_negocio) ON DELETE CASCADE,
    CONSTRAINT fk_calificacion_cita
        FOREIGN KEY (id_cita) REFERENCES citas(id_cita) ON DELETE SET NULL
);

CREATE TABLE favoritos (
    id_favorito        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario         BIGINT NOT NULL,
    id_negocio         BIGINT NOT NULL,
    fecha              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_usuario, id_negocio),
    CONSTRAINT fk_favorito_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_favorito_negocio
        FOREIGN KEY (id_negocio) REFERENCES negocios(id_negocio) ON DELETE CASCADE
);

-- =========================
-- PRODUCTOS, INVENTARIO
-- =========================

CREATE TABLE productos (
    id_producto        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_negocio         BIGINT NOT NULL,
    nombre             VARCHAR(150) NOT NULL,
    descripcion        TEXT,
    precio             NUMERIC(12,2) NOT NULL CHECK (precio >= 0),
    stock              INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    imagen_url         TEXT,
    estado             VARCHAR(20) NOT NULL DEFAULT 'activo'
                      CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_productos_negocio
        FOREIGN KEY (id_negocio) REFERENCES negocios(id_negocio) ON DELETE CASCADE
);

CREATE TABLE inventario_movimientos (
    id_movimiento      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_producto        BIGINT NOT NULL,
    tipo_movimiento    VARCHAR(20) NOT NULL
                      CHECK (tipo_movimiento IN ('entrada', 'salida', 'ajuste')),
    cantidad           INTEGER NOT NULL CHECK (cantidad > 0),
    motivo             VARCHAR(255),
    fecha              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_inventario_producto
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
);

-- =========================
-- CARRITO, PEDIDOS Y PAGOS
-- =========================

CREATE TABLE carritos (
    id_carrito         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario         BIGINT NOT NULL,
    estado             VARCHAR(20) NOT NULL DEFAULT 'activo'
                      CHECK (estado IN ('activo', 'cerrado', 'abandonado')),
    fecha_creacion     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_carrito_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE carrito_detalle (
    id_carrito_detalle BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_carrito         BIGINT NOT NULL,
    tipo_item          VARCHAR(20) NOT NULL
                      CHECK (tipo_item IN ('producto', 'servicio')),
    id_producto        BIGINT,
    id_servicio        BIGINT,
    cantidad           INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    precio_unitario    NUMERIC(12,2) NOT NULL CHECK (precio_unitario >= 0),
    CONSTRAINT chk_carrito_item
        CHECK (
            (tipo_item = 'producto' AND id_producto IS NOT NULL AND id_servicio IS NULL)
            OR
            (tipo_item = 'servicio' AND id_servicio IS NOT NULL AND id_producto IS NULL)
        ),
    CONSTRAINT fk_carrito_detalle_carrito
        FOREIGN KEY (id_carrito) REFERENCES carritos(id_carrito) ON DELETE CASCADE,
    CONSTRAINT fk_carrito_detalle_producto
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    CONSTRAINT fk_carrito_detalle_servicio
        FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio) ON DELETE CASCADE
);

CREATE TABLE pedidos (
    id_pedido          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario         BIGINT NOT NULL,
    id_negocio         BIGINT NOT NULL,
    total              NUMERIC(12,2) NOT NULL CHECK (total >= 0),
    estado             VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                      CHECK (estado IN ('pendiente', 'pagado', 'cancelado', 'entregado')),
    fecha              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pedido_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_pedido_negocio
        FOREIGN KEY (id_negocio) REFERENCES negocios(id_negocio) ON DELETE CASCADE
);

CREATE TABLE pedido_detalle (
    id_pedido_detalle  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_pedido          BIGINT NOT NULL,
    tipo_item          VARCHAR(20) NOT NULL
                      CHECK (tipo_item IN ('producto', 'servicio')),
    id_producto        BIGINT,
    id_servicio        BIGINT,
    cantidad           INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    precio_unitario    NUMERIC(12,2) NOT NULL CHECK (precio_unitario >= 0),
    subtotal           NUMERIC(12,2) NOT NULL CHECK (subtotal >= 0),
    CONSTRAINT chk_pedido_item
        CHECK (
            (tipo_item = 'producto' AND id_producto IS NOT NULL AND id_servicio IS NULL)
            OR
            (tipo_item = 'servicio' AND id_servicio IS NOT NULL AND id_producto IS NULL)
        ),
    CONSTRAINT fk_pedido_detalle_pedido
        FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    CONSTRAINT fk_pedido_detalle_producto
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE SET NULL,
    CONSTRAINT fk_pedido_detalle_servicio
        FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio) ON DELETE SET NULL
);

CREATE TABLE pagos (
    id_pago             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_pedido           BIGINT NOT NULL,
    metodo_pago         VARCHAR(30) NOT NULL
                       CHECK (metodo_pago IN ('payu', 'efectivo', 'tarjeta', 'transferencia')),
    referencia_externa  VARCHAR(150),
    estado_pago         VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                       CHECK (estado_pago IN ('pendiente', 'aprobado', 'rechazado', 'reembolsado')),
    valor               NUMERIC(12,2) NOT NULL CHECK (valor >= 0),
    fecha_pago          TIMESTAMP,
    respuesta_pasarela  TEXT,
    CONSTRAINT fk_pago_pedido
        FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE
);

-- =========================
-- NOTIFICACIONES Y AUDITORÍA
-- =========================

CREATE TABLE notificaciones (
    id_notificacion    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario         BIGINT NOT NULL,
    titulo             VARCHAR(150) NOT NULL,
    mensaje            TEXT NOT NULL,
    tipo               VARCHAR(30) NOT NULL
                      CHECK (tipo IN ('cita', 'pago', 'pedido', 'sistema', 'promocion')),
    leida              BOOLEAN NOT NULL DEFAULT FALSE,
    fecha              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notificacion_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE auditoria (
    id_auditoria       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario         BIGINT,
    accion             VARCHAR(100) NOT NULL,
    tabla_afectada     VARCHAR(100) NOT NULL,
    id_registro        BIGINT,
    detalle            TEXT,
    fecha              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_auditoria_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
);

-- =========================
-- ÍNDICES
-- =========================

CREATE INDEX idx_negocios_ciudad ON negocios(ciudad);
CREATE INDEX idx_negocios_estado ON negocios(estado);
CREATE INDEX idx_empleados_negocio ON empleados(id_negocio);
CREATE INDEX idx_servicios_negocio ON servicios(id_negocio);
CREATE INDEX idx_citas_cliente ON citas(id_cliente);
CREATE INDEX idx_citas_negocio ON citas(id_negocio);
CREATE INDEX idx_citas_empleado ON citas(id_empleado);
CREATE INDEX idx_citas_fecha ON citas(fecha);
CREATE INDEX idx_productos_negocio ON productos(id_negocio);
CREATE INDEX idx_pedidos_usuario ON pedidos(id_usuario);
CREATE INDEX idx_pagos_pedido ON pagos(id_pedido);
CREATE INDEX idx_notificaciones_usuario ON notificaciones(id_usuario);

-- =========================
-- DATOS BÁSICOS INICIALES
-- =========================

INSERT INTO roles (nombre, descripcion) VALUES
('cliente', 'Usuario cliente de la plataforma'),
('negocio', 'Propietario o administrador de negocio'),
('empleado', 'Empleado de un negocio'),
('admin', 'Administrador general del sistema')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO categorias_negocio (nombre, descripcion) VALUES
('barberia', 'Servicios de barbería'),
('peluqueria', 'Servicios de peluquería'),
('tatuajes', 'Servicios de tatuajes'),
('masajes', 'Servicios de masajes'),
('spa', 'Servicios de spa y estética')
ON CONFLICT (nombre) DO NOTHING;

COMMIT;