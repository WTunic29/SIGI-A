-- SIGI-A - Patch seguro para la BD actual en AWS
-- Corrige lo que faltaba para registro, activacion y MFA.

BEGIN;

-- 1) Permitir usuarios pendientes durante activacion por correo.
ALTER TABLE core.usuarios DROP CONSTRAINT IF EXISTS usuarios_estado_check;

ALTER TABLE core.usuarios
ADD CONSTRAINT usuarios_estado_check
CHECK (estado IN ('activo', 'inactivo', 'bloqueado', 'pendiente'));

-- 2) Columnas que espera el backend para MFA/TOTP.
ALTER TABLE core.usuarios
ADD COLUMN IF NOT EXISTS mfa_totp_enabled BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE core.usuarios
ADD COLUMN IF NOT EXISTS mfa_totp_secret VARCHAR(255);

-- 3) Tabla que espera el backend para links de activacion.
CREATE TABLE IF NOT EXISTS core.tokens_activacion (
    id_token BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario BIGINT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    usado BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_tokens_activacion_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES core.usuarios(id_usuario)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tokens_activacion_usuario
ON core.tokens_activacion(id_usuario);

CREATE INDEX IF NOT EXISTS idx_tokens_activacion_token
ON core.tokens_activacion(token);

COMMIT;
