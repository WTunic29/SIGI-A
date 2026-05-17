"""Verifica que el OpenAPI expone los prefijos principales del backend."""


def test_openapi_document_available(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    keys = "".join(paths.keys())
    for prefix in (
        "/auth",
        "/negocios",
        "/productos",
        "/pedidos",
        "/pagos",
        "/citas",
        "/empleados",
        "/servicios",
        "/notificaciones",
        "/calificaciones",
    ):
        assert prefix in keys, f"Falta ruta OpenAPI para {prefix}"
