#!/usr/bin/env python3
"""Falla si hay más xfail de los documentados en BACKEND_ISSUES_DETECTED.md."""

from __future__ import annotations

import re
import sys
from pathlib import Path

QA_ROOT = Path(__file__).resolve().parents[1]
TESTS = QA_ROOT / "tests"
# Presupuesto acordado: 1 xfail conocido (citas).
MAX_XFAIL = 1

PATTERN = re.compile(r"@pytest\.mark\.xfail\b")


def main() -> int:
    count = 0
    locations: list[str] = []
    for path in sorted(TESTS.rglob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        n = len(PATTERN.findall(text))
        if n:
            count += n
            locations.append(f"{path.relative_to(QA_ROOT)} ({n})")
    if count > MAX_XFAIL:
        print(
            f"check_xfail_budget: {count} @pytest.mark.xfail > máximo {MAX_XFAIL}",
            file=sys.stderr,
        )
        for loc in locations:
            print(f"  - {loc}", file=sys.stderr)
        print(
            "  Corrige el backend o actualiza BACKEND_ISSUES_DETECTED.md y MAX_XFAIL con justificación.",
            file=sys.stderr,
        )
        return 1
    print(f"check_xfail_budget: OK ({count}/{MAX_XFAIL} xfail)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
