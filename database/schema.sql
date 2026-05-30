--
-- PostgreSQL database dump
--

\restrict 9c7ARbRhz1xTncnQpwTkdTiavdv1NPATrqpBN5I3CUctrhDGfdr7eM3OT5iYCL0

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: core; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA core;


ALTER SCHEMA core OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auditoria; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.auditoria (
    id_auditoria bigint NOT NULL,
    id_usuario bigint,
    accion character varying(100) NOT NULL,
    tabla_afectada character varying(100) NOT NULL,
    id_registro bigint,
    detalle text,
    fecha timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE core.auditoria OWNER TO postgres;

--
-- Name: auditoria_id_auditoria_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.auditoria ALTER COLUMN id_auditoria ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.auditoria_id_auditoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: calificaciones; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.calificaciones (
    id_calificacion bigint NOT NULL,
    id_cliente bigint NOT NULL,
    id_negocio bigint NOT NULL,
    id_cita bigint,
    puntuacion smallint NOT NULL,
    comentario text,
    fecha timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT calificaciones_puntuacion_check CHECK (((puntuacion >= 1) AND (puntuacion <= 5)))
);


ALTER TABLE core.calificaciones OWNER TO postgres;

--
-- Name: calificaciones_id_calificacion_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.calificaciones ALTER COLUMN id_calificacion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.calificaciones_id_calificacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: carrito_detalle; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.carrito_detalle (
    id_carrito_detalle bigint NOT NULL,
    id_carrito bigint NOT NULL,
    tipo_item character varying(20) NOT NULL,
    id_producto bigint,
    id_servicio bigint,
    cantidad integer DEFAULT 1 NOT NULL,
    precio_unitario numeric(12,2) NOT NULL,
    CONSTRAINT carrito_detalle_cantidad_check CHECK ((cantidad > 0)),
    CONSTRAINT carrito_detalle_precio_unitario_check CHECK ((precio_unitario >= (0)::numeric)),
    CONSTRAINT carrito_detalle_tipo_item_check CHECK (((tipo_item)::text = ANY ((ARRAY['producto'::character varying, 'servicio'::character varying])::text[]))),
    CONSTRAINT chk_carrito_item CHECK (((((tipo_item)::text = 'producto'::text) AND (id_producto IS NOT NULL) AND (id_servicio IS NULL)) OR (((tipo_item)::text = 'servicio'::text) AND (id_servicio IS NOT NULL) AND (id_producto IS NULL))))
);


ALTER TABLE core.carrito_detalle OWNER TO postgres;

--
-- Name: carrito_detalle_id_carrito_detalle_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.carrito_detalle ALTER COLUMN id_carrito_detalle ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.carrito_detalle_id_carrito_detalle_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: carritos; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.carritos (
    id_carrito bigint NOT NULL,
    id_usuario bigint NOT NULL,
    estado character varying(20) DEFAULT 'activo'::character varying NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT carritos_estado_check CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'cerrado'::character varying, 'abandonado'::character varying])::text[])))
);


ALTER TABLE core.carritos OWNER TO postgres;

--
-- Name: carritos_id_carrito_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.carritos ALTER COLUMN id_carrito ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.carritos_id_carrito_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: categorias_negocio; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.categorias_negocio (
    id_categoria bigint NOT NULL,
    nombre character varying(80) NOT NULL,
    descripcion character varying(255)
);


ALTER TABLE core.categorias_negocio OWNER TO postgres;

--
-- Name: categorias_negocio_id_categoria_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.categorias_negocio ALTER COLUMN id_categoria ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.categorias_negocio_id_categoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: citas; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.citas (
    id_cita bigint NOT NULL,
    id_cliente bigint NOT NULL,
    id_negocio bigint NOT NULL,
    id_empleado bigint NOT NULL,
    fecha date NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    estado character varying(20) DEFAULT 'pendiente'::character varying NOT NULL,
    observaciones text,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_cita_horas CHECK ((hora_fin > hora_inicio)),
    CONSTRAINT citas_estado_check CHECK (((estado)::text = ANY ((ARRAY['pendiente'::character varying, 'confirmada'::character varying, 'cancelada'::character varying, 'completada'::character varying, 'no_asistio'::character varying])::text[])))
);


ALTER TABLE core.citas OWNER TO postgres;

--
-- Name: citas_id_cita_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.citas ALTER COLUMN id_cita ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.citas_id_cita_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: codigos_2fa; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.codigos_2fa (
    id_codigo integer NOT NULL,
    id_usuario integer NOT NULL,
    codigo character varying(6) NOT NULL,
    fecha_expiracion timestamp without time zone NOT NULL,
    usado boolean DEFAULT false NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE core.codigos_2fa OWNER TO postgres;

--
-- Name: codigos_2fa_id_codigo_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

CREATE SEQUENCE core.codigos_2fa_id_codigo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE core.codigos_2fa_id_codigo_seq OWNER TO postgres;

--
-- Name: codigos_2fa_id_codigo_seq; Type: SEQUENCE OWNED BY; Schema: core; Owner: postgres
--

ALTER SEQUENCE core.codigos_2fa_id_codigo_seq OWNED BY core.codigos_2fa.id_codigo;


--
-- Name: detalle_cita; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.detalle_cita (
    id_detalle_cita bigint NOT NULL,
    id_cita bigint NOT NULL,
    id_servicio bigint NOT NULL,
    precio numeric(12,2) NOT NULL,
    duracion integer NOT NULL,
    CONSTRAINT detalle_cita_duracion_check CHECK ((duracion > 0)),
    CONSTRAINT detalle_cita_precio_check CHECK ((precio >= (0)::numeric))
);


ALTER TABLE core.detalle_cita OWNER TO postgres;

--
-- Name: detalle_cita_id_detalle_cita_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.detalle_cita ALTER COLUMN id_detalle_cita ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.detalle_cita_id_detalle_cita_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: empleado_servicio; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.empleado_servicio (
    id_empleado_servicio bigint NOT NULL,
    id_empleado bigint NOT NULL,
    id_servicio bigint NOT NULL
);


ALTER TABLE core.empleado_servicio OWNER TO postgres;

--
-- Name: empleado_servicio_id_empleado_servicio_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.empleado_servicio ALTER COLUMN id_empleado_servicio ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.empleado_servicio_id_empleado_servicio_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: empleados; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.empleados (
    id_empleado bigint NOT NULL,
    id_negocio bigint NOT NULL,
    nombre character varying(100) NOT NULL,
    apellido character varying(100) NOT NULL,
    telefono character varying(30),
    email character varying(150),
    especialidad character varying(120),
    foto_url text,
    estado character varying(20) DEFAULT 'activo'::character varying NOT NULL,
    CONSTRAINT empleados_estado_check CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying])::text[])))
);


ALTER TABLE core.empleados OWNER TO postgres;

--
-- Name: empleados_id_empleado_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.empleados ALTER COLUMN id_empleado ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.empleados_id_empleado_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: favoritos; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.favoritos (
    id_favorito bigint NOT NULL,
    id_usuario bigint NOT NULL,
    id_negocio bigint NOT NULL,
    fecha timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE core.favoritos OWNER TO postgres;

--
-- Name: favoritos_id_favorito_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.favoritos ALTER COLUMN id_favorito ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.favoritos_id_favorito_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: horarios_empleado; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.horarios_empleado (
    id_horario bigint NOT NULL,
    id_empleado bigint NOT NULL,
    dia_semana smallint NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    disponible boolean DEFAULT true NOT NULL,
    CONSTRAINT chk_horario_valido CHECK ((hora_fin > hora_inicio)),
    CONSTRAINT horarios_empleado_dia_semana_check CHECK (((dia_semana >= 1) AND (dia_semana <= 7)))
);


ALTER TABLE core.horarios_empleado OWNER TO postgres;

--
-- Name: horarios_empleado_id_horario_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.horarios_empleado ALTER COLUMN id_horario ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.horarios_empleado_id_horario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: imagenes_negocio; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.imagenes_negocio (
    id_imagen bigint NOT NULL,
    id_negocio bigint NOT NULL,
    url_imagen text NOT NULL,
    descripcion character varying(255),
    principal boolean DEFAULT false NOT NULL
);


ALTER TABLE core.imagenes_negocio OWNER TO postgres;

--
-- Name: imagenes_negocio_id_imagen_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.imagenes_negocio ALTER COLUMN id_imagen ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.imagenes_negocio_id_imagen_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: inventario_movimientos; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.inventario_movimientos (
    id_movimiento bigint NOT NULL,
    id_producto bigint NOT NULL,
    tipo_movimiento character varying(20) NOT NULL,
    cantidad integer NOT NULL,
    motivo character varying(255),
    fecha timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT inventario_movimientos_cantidad_check CHECK ((cantidad > 0)),
    CONSTRAINT inventario_movimientos_tipo_movimiento_check CHECK (((tipo_movimiento)::text = ANY ((ARRAY['entrada'::character varying, 'salida'::character varying, 'ajuste'::character varying])::text[])))
);


ALTER TABLE core.inventario_movimientos OWNER TO postgres;

--
-- Name: inventario_movimientos_id_movimiento_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.inventario_movimientos ALTER COLUMN id_movimiento ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.inventario_movimientos_id_movimiento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: negocio_categoria; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.negocio_categoria (
    id_negocio_categoria bigint NOT NULL,
    id_negocio bigint NOT NULL,
    id_categoria bigint NOT NULL
);


ALTER TABLE core.negocio_categoria OWNER TO postgres;

--
-- Name: negocio_categoria_id_negocio_categoria_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.negocio_categoria ALTER COLUMN id_negocio_categoria ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.negocio_categoria_id_negocio_categoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: negocios; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.negocios (
    id_negocio bigint NOT NULL,
    id_usuario_propietario bigint NOT NULL,
    nombre_negocio character varying(150) NOT NULL,
    descripcion text,
    direccion character varying(255),
    ciudad character varying(100),
    latitud numeric(9,6),
    longitud numeric(9,6),
    telefono character varying(30),
    email_negocio character varying(150),
    logo_url text,
    color_primario character varying(20),
    color_secundario character varying(20),
    categoria_principal character varying(80),
    estado character varying(20) DEFAULT 'activo'::character varying NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT negocios_estado_check CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying, 'suspendido'::character varying])::text[])))
);


ALTER TABLE core.negocios OWNER TO postgres;

--
-- Name: negocios_id_negocio_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.negocios ALTER COLUMN id_negocio ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.negocios_id_negocio_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: notificaciones; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.notificaciones (
    id_notificacion bigint NOT NULL,
    id_usuario bigint NOT NULL,
    titulo character varying(150) NOT NULL,
    mensaje text NOT NULL,
    tipo character varying(30) NOT NULL,
    leida boolean DEFAULT false NOT NULL,
    fecha timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT notificaciones_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['cita'::character varying, 'pago'::character varying, 'pedido'::character varying, 'sistema'::character varying, 'promocion'::character varying])::text[])))
);


ALTER TABLE core.notificaciones OWNER TO postgres;

--
-- Name: notificaciones_id_notificacion_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.notificaciones ALTER COLUMN id_notificacion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.notificaciones_id_notificacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: pagos; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.pagos (
    id_pago bigint NOT NULL,
    id_pedido bigint NOT NULL,
    metodo_pago character varying(30) NOT NULL,
    referencia_externa character varying(150),
    estado_pago character varying(20) DEFAULT 'pendiente'::character varying NOT NULL,
    valor numeric(12,2) NOT NULL,
    fecha_pago timestamp without time zone,
    respuesta_pasarela text,
    CONSTRAINT pagos_estado_pago_check CHECK (((estado_pago)::text = ANY ((ARRAY['pendiente'::character varying, 'aprobado'::character varying, 'rechazado'::character varying, 'reembolsado'::character varying])::text[]))),
    CONSTRAINT pagos_metodo_pago_check CHECK (((metodo_pago)::text = ANY ((ARRAY['payu'::character varying, 'efectivo'::character varying, 'tarjeta'::character varying, 'transferencia'::character varying])::text[]))),
    CONSTRAINT pagos_valor_check CHECK ((valor >= (0)::numeric))
);


ALTER TABLE core.pagos OWNER TO postgres;

--
-- Name: pagos_id_pago_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.pagos ALTER COLUMN id_pago ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.pagos_id_pago_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: pedido_detalle; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.pedido_detalle (
    id_pedido_detalle bigint NOT NULL,
    id_pedido bigint NOT NULL,
    tipo_item character varying(20) NOT NULL,
    id_producto bigint,
    id_servicio bigint,
    cantidad integer DEFAULT 1 NOT NULL,
    precio_unitario numeric(12,2) NOT NULL,
    subtotal numeric(12,2) NOT NULL,
    CONSTRAINT chk_pedido_item CHECK (((((tipo_item)::text = 'producto'::text) AND (id_producto IS NOT NULL) AND (id_servicio IS NULL)) OR (((tipo_item)::text = 'servicio'::text) AND (id_servicio IS NOT NULL) AND (id_producto IS NULL)))),
    CONSTRAINT pedido_detalle_cantidad_check CHECK ((cantidad > 0)),
    CONSTRAINT pedido_detalle_precio_unitario_check CHECK ((precio_unitario >= (0)::numeric)),
    CONSTRAINT pedido_detalle_subtotal_check CHECK ((subtotal >= (0)::numeric)),
    CONSTRAINT pedido_detalle_tipo_item_check CHECK (((tipo_item)::text = ANY ((ARRAY['producto'::character varying, 'servicio'::character varying])::text[])))
);


ALTER TABLE core.pedido_detalle OWNER TO postgres;

--
-- Name: pedido_detalle_id_pedido_detalle_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.pedido_detalle ALTER COLUMN id_pedido_detalle ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.pedido_detalle_id_pedido_detalle_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: pedidos; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.pedidos (
    id_pedido bigint NOT NULL,
    id_usuario bigint NOT NULL,
    id_negocio bigint NOT NULL,
    total numeric(12,2) NOT NULL,
    estado character varying(20) DEFAULT 'pendiente'::character varying NOT NULL,
    fecha timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT pedidos_estado_check CHECK (((estado)::text = ANY ((ARRAY['pendiente'::character varying, 'pagado'::character varying, 'cancelado'::character varying, 'entregado'::character varying])::text[]))),
    CONSTRAINT pedidos_total_check CHECK ((total >= (0)::numeric))
);


ALTER TABLE core.pedidos OWNER TO postgres;

--
-- Name: pedidos_id_pedido_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.pedidos ALTER COLUMN id_pedido ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.pedidos_id_pedido_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: productos; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.productos (
    id_producto bigint NOT NULL,
    id_negocio bigint NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text,
    precio numeric(12,2) NOT NULL,
    stock integer DEFAULT 0 NOT NULL,
    imagen_url text,
    estado character varying(20) DEFAULT 'activo'::character varying NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT productos_estado_check CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying])::text[]))),
    CONSTRAINT productos_precio_check CHECK ((precio >= (0)::numeric)),
    CONSTRAINT productos_stock_check CHECK ((stock >= 0))
);


ALTER TABLE core.productos OWNER TO postgres;

--
-- Name: productos_id_producto_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.productos ALTER COLUMN id_producto ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.productos_id_producto_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: roles; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.roles (
    id_rol bigint NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion character varying(255)
);


ALTER TABLE core.roles OWNER TO postgres;

--
-- Name: roles_id_rol_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.roles ALTER COLUMN id_rol ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.roles_id_rol_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: servicios; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.servicios (
    id_servicio bigint NOT NULL,
    id_negocio bigint NOT NULL,
    nombre character varying(120) NOT NULL,
    descripcion text,
    duracion_minutos integer NOT NULL,
    precio numeric(12,2) NOT NULL,
    estado character varying(20) DEFAULT 'activo'::character varying NOT NULL,
    imagen_url text,
    CONSTRAINT servicios_duracion_minutos_check CHECK ((duracion_minutos > 0)),
    CONSTRAINT servicios_estado_check CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying])::text[]))),
    CONSTRAINT servicios_precio_check CHECK ((precio >= (0)::numeric))
);


ALTER TABLE core.servicios OWNER TO postgres;

--
-- Name: servicios_id_servicio_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.servicios ALTER COLUMN id_servicio ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.servicios_id_servicio_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: sesiones; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.sesiones (
    id_sesion bigint NOT NULL,
    id_usuario bigint NOT NULL,
    token character varying(500) NOT NULL,
    fecha_inicio timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_expiracion timestamp without time zone NOT NULL,
    ip character varying(50),
    user_agent text,
    activa boolean DEFAULT true NOT NULL
);


ALTER TABLE core.sesiones OWNER TO postgres;

--
-- Name: sesiones_id_sesion_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.sesiones ALTER COLUMN id_sesion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.sesiones_id_sesion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tokens_recuperacion; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.tokens_recuperacion (
    id_token bigint NOT NULL,
    id_usuario bigint NOT NULL,
    token character varying(255) NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_expiracion timestamp without time zone NOT NULL,
    usado boolean DEFAULT false NOT NULL
);


ALTER TABLE core.tokens_recuperacion OWNER TO postgres;

--
-- Name: tokens_recuperacion_id_token_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.tokens_recuperacion ALTER COLUMN id_token ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.tokens_recuperacion_id_token_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: usuario_rol; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.usuario_rol (
    id_usuario_rol bigint NOT NULL,
    id_usuario bigint NOT NULL,
    id_rol bigint NOT NULL
);


ALTER TABLE core.usuario_rol OWNER TO postgres;

--
-- Name: usuario_rol_id_usuario_rol_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.usuario_rol ALTER COLUMN id_usuario_rol ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.usuario_rol_id_usuario_rol_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: usuarios; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.usuarios (
    id_usuario bigint NOT NULL,
    nombre character varying(100) NOT NULL,
    apellido character varying(100) NOT NULL,
    correo character varying(150) NOT NULL,
    telefono character varying(30),
    password_hash character varying(255) NOT NULL,
    estado character varying(20) DEFAULT 'activo'::character varying NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ultimo_login timestamp without time zone,
    rol character varying(20) DEFAULT 'cliente'::character varying NOT NULL,
    mfa_totp_enabled boolean DEFAULT false NOT NULL,
    mfa_totp_secret character varying(255),
    CONSTRAINT usuarios_estado_check CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying, 'bloqueado'::character varying, 'pendiente'::character varying])::text[])))
);


ALTER TABLE core.usuarios OWNER TO postgres;

--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.usuarios ALTER COLUMN id_usuario ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.usuarios_id_usuario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tokens_activacion; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.tokens_activacion (
    id_token bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    id_usuario bigint NOT NULL,
    token character varying(255) NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_expiracion timestamp without time zone NOT NULL,
    usado boolean DEFAULT false NOT NULL
);


ALTER TABLE core.tokens_activacion OWNER TO postgres;


--
-- Name: verificacion_2fa; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.verificacion_2fa (
    id_verificacion bigint NOT NULL,
    id_usuario bigint NOT NULL,
    codigo character varying(20) NOT NULL,
    metodo character varying(20) DEFAULT 'email'::character varying NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_expiracion timestamp without time zone NOT NULL,
    usado boolean DEFAULT false NOT NULL,
    CONSTRAINT verificacion_2fa_metodo_check CHECK (((metodo)::text = ANY ((ARRAY['email'::character varying, 'sms'::character varying, 'app'::character varying])::text[])))
);


ALTER TABLE core.verificacion_2fa OWNER TO postgres;

--
-- Name: verificacion_2fa_id_verificacion_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

ALTER TABLE core.verificacion_2fa ALTER COLUMN id_verificacion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME core.verificacion_2fa_id_verificacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: codigos_2fa id_codigo; Type: DEFAULT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.codigos_2fa ALTER COLUMN id_codigo SET DEFAULT nextval('core.codigos_2fa_id_codigo_seq'::regclass);


--
-- Name: auditoria auditoria_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.auditoria
    ADD CONSTRAINT auditoria_pkey PRIMARY KEY (id_auditoria);


--
-- Name: calificaciones calificaciones_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.calificaciones
    ADD CONSTRAINT calificaciones_pkey PRIMARY KEY (id_calificacion);


--
-- Name: carrito_detalle carrito_detalle_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.carrito_detalle
    ADD CONSTRAINT carrito_detalle_pkey PRIMARY KEY (id_carrito_detalle);


--
-- Name: carritos carritos_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.carritos
    ADD CONSTRAINT carritos_pkey PRIMARY KEY (id_carrito);


--
-- Name: categorias_negocio categorias_negocio_nombre_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.categorias_negocio
    ADD CONSTRAINT categorias_negocio_nombre_key UNIQUE (nombre);


--
-- Name: categorias_negocio categorias_negocio_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.categorias_negocio
    ADD CONSTRAINT categorias_negocio_pkey PRIMARY KEY (id_categoria);


--
-- Name: citas citas_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.citas
    ADD CONSTRAINT citas_pkey PRIMARY KEY (id_cita);


--
-- Name: codigos_2fa codigos_2fa_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.codigos_2fa
    ADD CONSTRAINT codigos_2fa_pkey PRIMARY KEY (id_codigo);


--
-- Name: detalle_cita detalle_cita_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.detalle_cita
    ADD CONSTRAINT detalle_cita_pkey PRIMARY KEY (id_detalle_cita);


--
-- Name: empleado_servicio empleado_servicio_id_empleado_id_servicio_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.empleado_servicio
    ADD CONSTRAINT empleado_servicio_id_empleado_id_servicio_key UNIQUE (id_empleado, id_servicio);


--
-- Name: empleado_servicio empleado_servicio_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.empleado_servicio
    ADD CONSTRAINT empleado_servicio_pkey PRIMARY KEY (id_empleado_servicio);


--
-- Name: empleados empleados_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.empleados
    ADD CONSTRAINT empleados_pkey PRIMARY KEY (id_empleado);


--
-- Name: favoritos favoritos_id_usuario_id_negocio_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.favoritos
    ADD CONSTRAINT favoritos_id_usuario_id_negocio_key UNIQUE (id_usuario, id_negocio);


--
-- Name: favoritos favoritos_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.favoritos
    ADD CONSTRAINT favoritos_pkey PRIMARY KEY (id_favorito);


--
-- Name: horarios_empleado horarios_empleado_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.horarios_empleado
    ADD CONSTRAINT horarios_empleado_pkey PRIMARY KEY (id_horario);


--
-- Name: imagenes_negocio imagenes_negocio_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.imagenes_negocio
    ADD CONSTRAINT imagenes_negocio_pkey PRIMARY KEY (id_imagen);


--
-- Name: inventario_movimientos inventario_movimientos_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.inventario_movimientos
    ADD CONSTRAINT inventario_movimientos_pkey PRIMARY KEY (id_movimiento);


--
-- Name: negocio_categoria negocio_categoria_id_negocio_id_categoria_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.negocio_categoria
    ADD CONSTRAINT negocio_categoria_id_negocio_id_categoria_key UNIQUE (id_negocio, id_categoria);


--
-- Name: negocio_categoria negocio_categoria_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.negocio_categoria
    ADD CONSTRAINT negocio_categoria_pkey PRIMARY KEY (id_negocio_categoria);


--
-- Name: negocios negocios_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.negocios
    ADD CONSTRAINT negocios_pkey PRIMARY KEY (id_negocio);


--
-- Name: notificaciones notificaciones_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.notificaciones
    ADD CONSTRAINT notificaciones_pkey PRIMARY KEY (id_notificacion);


--
-- Name: pagos pagos_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.pagos
    ADD CONSTRAINT pagos_pkey PRIMARY KEY (id_pago);


--
-- Name: pedido_detalle pedido_detalle_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.pedido_detalle
    ADD CONSTRAINT pedido_detalle_pkey PRIMARY KEY (id_pedido_detalle);


--
-- Name: pedidos pedidos_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.pedidos
    ADD CONSTRAINT pedidos_pkey PRIMARY KEY (id_pedido);


--
-- Name: productos productos_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.productos
    ADD CONSTRAINT productos_pkey PRIMARY KEY (id_producto);


--
-- Name: roles roles_nombre_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.roles
    ADD CONSTRAINT roles_nombre_key UNIQUE (nombre);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id_rol);


--
-- Name: servicios servicios_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.servicios
    ADD CONSTRAINT servicios_pkey PRIMARY KEY (id_servicio);


--
-- Name: sesiones sesiones_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sesiones
    ADD CONSTRAINT sesiones_pkey PRIMARY KEY (id_sesion);


--
-- Name: sesiones sesiones_token_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sesiones
    ADD CONSTRAINT sesiones_token_key UNIQUE (token);


--
-- Name: tokens_activacion tokens_activacion_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.tokens_activacion
    ADD CONSTRAINT tokens_activacion_pkey PRIMARY KEY (id_token);


--
-- Name: tokens_activacion tokens_activacion_token_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.tokens_activacion
    ADD CONSTRAINT tokens_activacion_token_key UNIQUE (token);


--
-- Name: tokens_recuperacion tokens_recuperacion_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.tokens_recuperacion
    ADD CONSTRAINT tokens_recuperacion_pkey PRIMARY KEY (id_token);


--
-- Name: tokens_recuperacion tokens_recuperacion_token_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.tokens_recuperacion
    ADD CONSTRAINT tokens_recuperacion_token_key UNIQUE (token);


--
-- Name: usuario_rol usuario_rol_id_usuario_id_rol_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.usuario_rol
    ADD CONSTRAINT usuario_rol_id_usuario_id_rol_key UNIQUE (id_usuario, id_rol);


--
-- Name: usuario_rol usuario_rol_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.usuario_rol
    ADD CONSTRAINT usuario_rol_pkey PRIMARY KEY (id_usuario_rol);


--
-- Name: usuarios usuarios_correo_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.usuarios
    ADD CONSTRAINT usuarios_correo_key UNIQUE (correo);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);


--
-- Name: verificacion_2fa verificacion_2fa_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.verificacion_2fa
    ADD CONSTRAINT verificacion_2fa_pkey PRIMARY KEY (id_verificacion);


--
-- Name: idx_citas_cliente; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_citas_cliente ON core.citas USING btree (id_cliente);


--
-- Name: idx_citas_empleado; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_citas_empleado ON core.citas USING btree (id_empleado);


--
-- Name: idx_citas_fecha; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_citas_fecha ON core.citas USING btree (fecha);


--
-- Name: idx_citas_negocio; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_citas_negocio ON core.citas USING btree (id_negocio);


--
-- Name: idx_empleados_negocio; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_empleados_negocio ON core.empleados USING btree (id_negocio);


--
-- Name: idx_negocios_ciudad; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_negocios_ciudad ON core.negocios USING btree (ciudad);


--
-- Name: idx_negocios_estado; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_negocios_estado ON core.negocios USING btree (estado);


--
-- Name: idx_notificaciones_usuario; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_notificaciones_usuario ON core.notificaciones USING btree (id_usuario);


--
-- Name: idx_pagos_pedido; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_pagos_pedido ON core.pagos USING btree (id_pedido);


--
-- Name: idx_pedidos_usuario; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_pedidos_usuario ON core.pedidos USING btree (id_usuario);


--
-- Name: idx_productos_negocio; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_productos_negocio ON core.productos USING btree (id_negocio);


--
-- Name: idx_servicios_negocio; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_servicios_negocio ON core.servicios USING btree (id_negocio);


--
-- Name: auditoria fk_auditoria_usuario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.auditoria
    ADD CONSTRAINT fk_auditoria_usuario FOREIGN KEY (id_usuario) REFERENCES core.usuarios(id_usuario) ON DELETE SET NULL;


--
-- Name: calificaciones fk_calificacion_cita; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.calificaciones
    ADD CONSTRAINT fk_calificacion_cita FOREIGN KEY (id_cita) REFERENCES core.citas(id_cita) ON DELETE SET NULL;


--
-- Name: calificaciones fk_calificacion_cliente; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.calificaciones
    ADD CONSTRAINT fk_calificacion_cliente FOREIGN KEY (id_cliente) REFERENCES core.usuarios(id_usuario);


--
-- Name: calificaciones fk_calificacion_negocio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.calificaciones
    ADD CONSTRAINT fk_calificacion_negocio FOREIGN KEY (id_negocio) REFERENCES core.negocios(id_negocio) ON DELETE CASCADE;


--
-- Name: carrito_detalle fk_carrito_detalle_carrito; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.carrito_detalle
    ADD CONSTRAINT fk_carrito_detalle_carrito FOREIGN KEY (id_carrito) REFERENCES core.carritos(id_carrito) ON DELETE CASCADE;


--
-- Name: carrito_detalle fk_carrito_detalle_producto; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.carrito_detalle
    ADD CONSTRAINT fk_carrito_detalle_producto FOREIGN KEY (id_producto) REFERENCES core.productos(id_producto) ON DELETE CASCADE;


--
-- Name: carrito_detalle fk_carrito_detalle_servicio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.carrito_detalle
    ADD CONSTRAINT fk_carrito_detalle_servicio FOREIGN KEY (id_servicio) REFERENCES core.servicios(id_servicio) ON DELETE CASCADE;


--
-- Name: carritos fk_carrito_usuario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.carritos
    ADD CONSTRAINT fk_carrito_usuario FOREIGN KEY (id_usuario) REFERENCES core.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: citas fk_citas_cliente; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.citas
    ADD CONSTRAINT fk_citas_cliente FOREIGN KEY (id_cliente) REFERENCES core.usuarios(id_usuario);


--
-- Name: citas fk_citas_empleado; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.citas
    ADD CONSTRAINT fk_citas_empleado FOREIGN KEY (id_empleado) REFERENCES core.empleados(id_empleado) ON DELETE CASCADE;


--
-- Name: citas fk_citas_negocio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.citas
    ADD CONSTRAINT fk_citas_negocio FOREIGN KEY (id_negocio) REFERENCES core.negocios(id_negocio) ON DELETE CASCADE;


--
-- Name: codigos_2fa fk_codigos_2fa_usuario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.codigos_2fa
    ADD CONSTRAINT fk_codigos_2fa_usuario FOREIGN KEY (id_usuario) REFERENCES core.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: detalle_cita fk_detalle_cita_cita; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.detalle_cita
    ADD CONSTRAINT fk_detalle_cita_cita FOREIGN KEY (id_cita) REFERENCES core.citas(id_cita) ON DELETE CASCADE;


--
-- Name: detalle_cita fk_detalle_cita_servicio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.detalle_cita
    ADD CONSTRAINT fk_detalle_cita_servicio FOREIGN KEY (id_servicio) REFERENCES core.servicios(id_servicio);


--
-- Name: empleado_servicio fk_empleado_servicio_empleado; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.empleado_servicio
    ADD CONSTRAINT fk_empleado_servicio_empleado FOREIGN KEY (id_empleado) REFERENCES core.empleados(id_empleado) ON DELETE CASCADE;


--
-- Name: empleado_servicio fk_empleado_servicio_servicio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.empleado_servicio
    ADD CONSTRAINT fk_empleado_servicio_servicio FOREIGN KEY (id_servicio) REFERENCES core.servicios(id_servicio) ON DELETE CASCADE;


--
-- Name: empleados fk_empleados_negocio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.empleados
    ADD CONSTRAINT fk_empleados_negocio FOREIGN KEY (id_negocio) REFERENCES core.negocios(id_negocio) ON DELETE CASCADE;


--
-- Name: favoritos fk_favorito_negocio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.favoritos
    ADD CONSTRAINT fk_favorito_negocio FOREIGN KEY (id_negocio) REFERENCES core.negocios(id_negocio) ON DELETE CASCADE;


--
-- Name: favoritos fk_favorito_usuario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.favoritos
    ADD CONSTRAINT fk_favorito_usuario FOREIGN KEY (id_usuario) REFERENCES core.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: horarios_empleado fk_horarios_empleado; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.horarios_empleado
    ADD CONSTRAINT fk_horarios_empleado FOREIGN KEY (id_empleado) REFERENCES core.empleados(id_empleado) ON DELETE CASCADE;


--
-- Name: imagenes_negocio fk_imagenes_negocio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.imagenes_negocio
    ADD CONSTRAINT fk_imagenes_negocio FOREIGN KEY (id_negocio) REFERENCES core.negocios(id_negocio) ON DELETE CASCADE;


--
-- Name: inventario_movimientos fk_inventario_producto; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.inventario_movimientos
    ADD CONSTRAINT fk_inventario_producto FOREIGN KEY (id_producto) REFERENCES core.productos(id_producto) ON DELETE CASCADE;


--
-- Name: negocio_categoria fk_negocio_categoria_categoria; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.negocio_categoria
    ADD CONSTRAINT fk_negocio_categoria_categoria FOREIGN KEY (id_categoria) REFERENCES core.categorias_negocio(id_categoria) ON DELETE CASCADE;


--
-- Name: negocio_categoria fk_negocio_categoria_negocio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.negocio_categoria
    ADD CONSTRAINT fk_negocio_categoria_negocio FOREIGN KEY (id_negocio) REFERENCES core.negocios(id_negocio) ON DELETE CASCADE;


--
-- Name: negocios fk_negocios_propietario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.negocios
    ADD CONSTRAINT fk_negocios_propietario FOREIGN KEY (id_usuario_propietario) REFERENCES core.usuarios(id_usuario);


--
-- Name: notificaciones fk_notificacion_usuario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.notificaciones
    ADD CONSTRAINT fk_notificacion_usuario FOREIGN KEY (id_usuario) REFERENCES core.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: pagos fk_pago_pedido; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.pagos
    ADD CONSTRAINT fk_pago_pedido FOREIGN KEY (id_pedido) REFERENCES core.pedidos(id_pedido) ON DELETE CASCADE;


--
-- Name: pedido_detalle fk_pedido_detalle_pedido; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.pedido_detalle
    ADD CONSTRAINT fk_pedido_detalle_pedido FOREIGN KEY (id_pedido) REFERENCES core.pedidos(id_pedido) ON DELETE CASCADE;


--
-- Name: pedido_detalle fk_pedido_detalle_producto; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.pedido_detalle
    ADD CONSTRAINT fk_pedido_detalle_producto FOREIGN KEY (id_producto) REFERENCES core.productos(id_producto) ON DELETE SET NULL;


--
-- Name: pedido_detalle fk_pedido_detalle_servicio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.pedido_detalle
    ADD CONSTRAINT fk_pedido_detalle_servicio FOREIGN KEY (id_servicio) REFERENCES core.servicios(id_servicio) ON DELETE SET NULL;


--
-- Name: pedidos fk_pedido_negocio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.pedidos
    ADD CONSTRAINT fk_pedido_negocio FOREIGN KEY (id_negocio) REFERENCES core.negocios(id_negocio) ON DELETE CASCADE;


--
-- Name: pedidos fk_pedido_usuario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.pedidos
    ADD CONSTRAINT fk_pedido_usuario FOREIGN KEY (id_usuario) REFERENCES core.usuarios(id_usuario);


--
-- Name: productos fk_productos_negocio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.productos
    ADD CONSTRAINT fk_productos_negocio FOREIGN KEY (id_negocio) REFERENCES core.negocios(id_negocio) ON DELETE CASCADE;


--
-- Name: servicios fk_servicios_negocio; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.servicios
    ADD CONSTRAINT fk_servicios_negocio FOREIGN KEY (id_negocio) REFERENCES core.negocios(id_negocio) ON DELETE CASCADE;


--
-- Name: sesiones fk_sesiones_usuario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sesiones
    ADD CONSTRAINT fk_sesiones_usuario FOREIGN KEY (id_usuario) REFERENCES core.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: tokens_recuperacion fk_tokens_usuario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.tokens_recuperacion
    ADD CONSTRAINT fk_tokens_usuario FOREIGN KEY (id_usuario) REFERENCES core.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: tokens_activacion fk_tokens_activacion_usuario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.tokens_activacion
    ADD CONSTRAINT fk_tokens_activacion_usuario FOREIGN KEY (id_usuario) REFERENCES core.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: usuario_rol fk_usuario_rol_rol; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.usuario_rol
    ADD CONSTRAINT fk_usuario_rol_rol FOREIGN KEY (id_rol) REFERENCES core.roles(id_rol) ON DELETE CASCADE;


--
-- Name: usuario_rol fk_usuario_rol_usuario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.usuario_rol
    ADD CONSTRAINT fk_usuario_rol_usuario FOREIGN KEY (id_usuario) REFERENCES core.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: verificacion_2fa fk_verificacion_usuario; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.verificacion_2fa
    ADD CONSTRAINT fk_verificacion_usuario FOREIGN KEY (id_usuario) REFERENCES core.usuarios(id_usuario) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 9c7ARbRhz1xTncnQpwTkdTiavdv1NPATrqpBN5I3CUctrhDGfdr7eM3OT5iYCL0

