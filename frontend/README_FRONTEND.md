# Frontend SIGI-A organizado por vistas

Este frontend conserva el diseño original, pero agrega páginas separadas para los flujos principales:

- `index.html`: landing pública.
- `login.html`: inicio de sesión.
- `registro.html`: registro.
- `mfa.html`: configuración inicial de MFA con QR.
- `verificar-mfa.html`: verificación MFA al iniciar sesión con app autenticadora.
- `usuario.html`: panel de cliente/usuario.
- `negocio.html`: panel de negocio.
- `superusuario.html`: panel de administración/superusuario.

## Flujo esperado

1. Registro crea usuario pendiente y envía correo de activación.
2. Login con usuario activo sin MFA redirige a `mfa.html`.
3. `mfa.html` consume `POST /auth/mfa/setup` y `POST /auth/mfa/confirm`.
4. Usuario con MFA activo en login pasa por `verificar-mfa.html`.
5. Después de verificar, se redirige por rol a `usuario.html`, `negocio.html` o `superusuario.html`.

## Despliegue

```bash
docker compose up -d --build frontend
```

Para evitar caché del navegador se agregó versión al script `main.js`.
