"""Prefijos OpenAPI que la suite QA espera en /openapi.json (contrato mínimo)."""

# Rutas montadas en backend/app/main.py — mantener alineado leyendo main.py, sin importar backend aquí.
OPENAPI_REQUIRED_PREFIXES: tuple[str, ...] = (
    "/auth",
    "/negocios",
    "/productos",
    "/servicios",
    "/empleados",
    "/empleado-servicio",
    "/horarios-empleado",
    "/citas",
    "/calificaciones",
    "/inventario-movimientos",
    "/notificaciones",
    "/pedidos",
    "/pagos",
    "/carritos",
    "/facturas",
    "/favoritos",
)

# Documentados para ampliar Postman/pytest; no fallan la suite si faltan en OpenAPI.
OPENAPI_OPTIONAL_PREFIXES: tuple[str, ...] = (
    "/pedido-detalle",
    "/carrito-detalle",
    "/tokens-recuperacion",
    "/sesiones",
    "/auditoria",
)
