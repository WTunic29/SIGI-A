"""fix mfa activation schema

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-30
"""

from alembic import op


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    ALTER TABLE core.usuarios DROP CONSTRAINT IF EXISTS usuarios_estado_check;
    """)

    op.execute("""
    ALTER TABLE core.usuarios
    ADD CONSTRAINT usuarios_estado_check
    CHECK (estado IN ('activo', 'inactivo', 'bloqueado', 'pendiente'));
    """)

    op.execute("""
    ALTER TABLE core.usuarios
    ADD COLUMN IF NOT EXISTS mfa_totp_enabled BOOLEAN NOT NULL DEFAULT FALSE;
    """)

    op.execute("""
    ALTER TABLE core.usuarios
    ADD COLUMN IF NOT EXISTS mfa_totp_secret VARCHAR(255);
    """)

    op.execute("""
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
    """)

    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_tokens_activacion_usuario
    ON core.tokens_activacion(id_usuario);
    """)

    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_tokens_activacion_token
    ON core.tokens_activacion(token);
    """)


def downgrade():
    op.execute("""
    DROP INDEX IF EXISTS core.idx_tokens_activacion_token;
    """)

    op.execute("""
    DROP INDEX IF EXISTS core.idx_tokens_activacion_usuario;
    """)

    op.execute("""
    DROP TABLE IF EXISTS core.tokens_activacion;
    """)

    op.execute("""
    ALTER TABLE core.usuarios
    DROP COLUMN IF EXISTS mfa_totp_secret;
    """)

    op.execute("""
    ALTER TABLE core.usuarios
    DROP COLUMN IF EXISTS mfa_totp_enabled;
    """)

    op.execute("""
    ALTER TABLE core.usuarios DROP CONSTRAINT IF EXISTS usuarios_estado_check;
    """)

    op.execute("""
    ALTER TABLE core.usuarios
    ADD CONSTRAINT usuarios_estado_check
    CHECK (estado IN ('activo', 'inactivo', 'bloqueado'));
    """)
