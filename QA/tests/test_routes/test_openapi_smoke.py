"""Verifica que el OpenAPI expone los prefijos principales del backend."""

import pytest

from tests.contract.openapi_prefixes import OPENAPI_REQUIRED_PREFIXES


@pytest.mark.contract
def test_openapi_document_available(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    keys = "".join(paths.keys())
    for prefix in OPENAPI_REQUIRED_PREFIXES:
        assert prefix in keys, f"Falta ruta OpenAPI para {prefix}"
