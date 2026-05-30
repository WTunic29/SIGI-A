#!/usr/bin/env bash
# Aplica migración carrito/checkout/facturas en PostgreSQL (Linux / AWS).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: define DATABASE_URL en backend/.env" >&2
  exit 1
fi

echo ">> Alembic upgrade (revision c3d4e5f6a7b8)"
alembic upgrade head

echo ">> Migración aplicada."
