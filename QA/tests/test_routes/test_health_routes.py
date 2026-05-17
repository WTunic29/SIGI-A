"""Contratos mínimos de raíz y diagnóstico de BD."""


class TestHealthRoutes:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "message" in r.json()
        assert "SIGI-A" in r.json()["message"]

    def test_test_db(self, client):
        r = client.get("/test-db")
        assert r.status_code == 200
        data = r.json()
        assert data.get("database") == "conectada"
        assert data.get("resultado") == 1
