#!/usr/bin/env bash
# SIGI-A QA — check (pytest + validadores) | smoke (Newman) | install (pnpm)
set -euo pipefail
cd "$(dirname "$0")"
CMD="${1:-check}"
shift || true

case "$CMD" in
  check)
    python scripts/validate_postman_workspace.py
    python scripts/check_xfail_budget.py
    exec python -m pytest tests -q --tb=line "$@"
    ;;
  smoke)
    if command -v pnpm >/dev/null; then
      PNPM=(pnpm)
    else
      echo "pnpm no en PATH; usando npx pnpm@9.15.9"
      PNPM=(npx --yes pnpm@9.15.9)
    fi
    [[ -d node_modules ]] || "${PNPM[@]}" install
    exec "${PNPM[@]}" run postman:newman:smoke "$@"
    ;;
  install)
    if command -v pnpm >/dev/null; then
      pnpm install
    else
      npx --yes pnpm@9.15.9 install
    fi
    echo "Python: pip install -r ../backend/requirements.txt -r requirements-ci.txt"
    ;;
  *)
    echo "Usage: $0 {check|smoke|install} [args...]"
    exit 1
    ;;
esac
