#!/usr/bin/env python3
"""
Valida fragmentos YAML del workspace Postman (QA/postman/collections/SIGI-A).

- Cada *.request.yaml: $kind, method, url, order entero; orders únicos.
- Placeholders {{var}} en url/cuerpo/descripciones deben existir en entornos o en
  .resources/definition.yaml (variables de colección).
- Los dos entornos principales deben declarar el mismo conjunto de claves.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

QA_ROOT = Path(__file__).resolve().parents[1]
COLLECTION_ROOT = QA_ROOT / "postman" / "collections" / "SIGI-A"
ENV_PATHS = [
    QA_ROOT / "postman" / "environments" / "SIGI-A-Local.env.yaml",
    QA_ROOT / "postman" / "environments" / "SIGI-A.environment.yaml",
]
DEFINITION_PATH = COLLECTION_ROOT / ".resources" / "definition.yaml"

VAR_RE = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}")


def _load_yaml(path: Path) -> tuple[dict | None, str | None]:
    if not path.exists():
        return None, f"archivo inexistente: {path}"
    raw = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        return None, f"YAML inválido {path}: {exc}"
    if data is None:
        return {}, None
    if not isinstance(data, dict):
        return None, f"raíz debe ser objeto en {path}"
    return data, None


def _env_keys(doc: dict) -> set[str]:
    keys = set()
    for item in doc.get("values") or []:
        k = item.get("key")
        if isinstance(k, str):
            keys.add(k)
    return keys


def _definition_var_keys(doc: dict) -> set[str]:
    keys = set()
    for item in doc.get("variables") or []:
        k = item.get("key")
        if isinstance(k, str):
            keys.add(k)
    return keys


def _gather_text_chunks(node) -> list[str]:
    """Recoge strings relevantes donde suele aparecer {{var}}."""
    out: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "scripts" or k == "code":
                continue
            out.extend(_gather_text_chunks(v))
    elif isinstance(node, list):
        for item in node:
            out.extend(_gather_text_chunks(item))
    elif isinstance(node, str):
        out.append(node)
    elif isinstance(node, (int, float, bool)):
        out.append(str(node))
    return out


def _gather_script_chunks(node) -> list[str]:
    """Incluye textos dentro de scripts (pueden tener place holders en algunos setups)."""
    out: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "code" and isinstance(v, str):
                out.append(v)
            else:
                out.extend(_gather_script_chunks(v))
    elif isinstance(node, list):
        for item in node:
            out.extend(_gather_script_chunks(item))
    return out


def _vars_in_request(doc: dict) -> set[str]:
    texts = _gather_text_chunks(doc) + _gather_script_chunks(doc.get("scripts"))
    keys = set()
    for text in texts:
        keys.update(VAR_RE.findall(text))
    return keys


def main() -> int:
    errors: list[str] = []

    if not COLLECTION_ROOT.is_dir():
        errors.append(f"No existe la carpeta de colección: {COLLECTION_ROOT}")
        return _report(errors)

    env_key_sets: list[tuple[Path, set[str]]] = []
    for ep in ENV_PATHS:
        doc, yaml_err = _load_yaml(ep)
        if yaml_err:
            errors.append(yaml_err)
            env_key_sets.append((ep, set()))
            continue
        env_key_sets.append((ep, _env_keys(doc or {})))

    if len(env_key_sets) == 2:
        (p1, k1), (p2, k2) = env_key_sets
        if k1 != k2:
            only1, only2 = sorted(k1 - k2), sorted(k2 - k1)
            errors.append(
                f"Claves de entorno distintas:\n  solo {p1.name}: {only1}\n  solo {p2.name}: {only2}"
            )

    known = set()
    for _, ks in env_key_sets:
        known |= ks
    def_doc, def_err = _load_yaml(DEFINITION_PATH)
    if def_err:
        errors.append(def_err)
    elif def_doc:
        known |= _definition_var_keys(def_doc)

    # Postman / Newman reservan $*
    def _ok(name: str) -> bool:
        return name in known

    seen_paths: set[Path] = set()
    orders: dict[int, str] = {}
    request_files: list[Path] = []

    for p in sorted(COLLECTION_ROOT.rglob("*.request.yaml")):
        rp = p.resolve()
        if rp in seen_paths:
            continue
        seen_paths.add(rp)
        if ".resources" in p.parts:
            continue
        request_files.append(p)

    for p in request_files:
        doc, yaml_err = _load_yaml(p)
        if yaml_err:
            errors.append(yaml_err)
            continue
        assert doc is not None
        kind = doc.get("$kind")
        if kind != "http-request":
            errors.append(f"{p.relative_to(QA_ROOT)}: $kind debe ser 'http-request', es {kind!r}")
            continue
        for field in ("method", "url", "order"):
            if field not in doc:
                errors.append(f"{p.relative_to(QA_ROOT)}: falta clave obligatoria '{field}'")
        order = doc.get("order")
        if order is not None and not isinstance(order, int):
            errors.append(
                f"{p.relative_to(QA_ROOT)}: 'order' debe ser int, es {type(order).__name__}"
            )
        elif isinstance(order, int):
            rel = str(p.relative_to(QA_ROOT))
            if order in orders and orders[order] != rel:
                errors.append(f"order duplicado {order}: {orders[order]} y {rel}")
            else:
                orders[order] = rel

        missing = sorted(v for v in _vars_in_request(doc) if not _ok(v))
        if missing:
            errors.append(
                f"{p.relative_to(QA_ROOT)}: variables no declaradas en env/definition: {missing}"
            )

    if not request_files:
        errors.append(f"No se encontraron *.request.yaml bajo {COLLECTION_ROOT}")

    return _report(errors)


def _report(errors: list[str]) -> int:
    if errors:
        print("validate_postman_workspace: FALLOS", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("validate_postman_workspace: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
