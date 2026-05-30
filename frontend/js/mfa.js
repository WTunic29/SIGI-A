const API_BASE = window.SIGIA_API_BASE || "http://3.15.197.152:10000";

    const token = localStorage.getItem("access_token");
    const usuarioRaw = localStorage.getItem("usuario");

    const msg = document.getElementById("msg");
    const qrBox = document.getElementById("qrBox");
    const secretBox = document.getElementById("secretBox");

    function mostrarMensaje(texto, ok = false) {
      msg.textContent = texto;
      msg.className = ok ? "msg success" : "msg";
    }

    function normalizarRol(rol) {
      const value = String(rol || "cliente").trim().toLowerCase();
      if (["usuario", "user", "cliente"].includes(value)) return "cliente";
      if (["administrador", "superusuario", "superuser", "super_admin", "super-admin", "admin"].includes(value)) return "admin";
      if (value === "negocio") return "negocio";
      return "cliente";
    }

    function irDashboardPorRol() {
      let usuario = {};
      try {
        usuario = JSON.parse(localStorage.getItem("usuario") || "{}");
      } catch {}

      const rol = normalizarRol(usuario.rol);

      if (rol === "negocio") {
        window.location.href = "negocio.html";
      } else if (rol === "admin") {
        window.location.href = "superusuario.html";
      } else {
        window.location.href = "usuario.html";
      }
    }

    async function cargarQR() {
      if (!token) {
        window.location.href = "login.html";
        return;
      }

      try {
        const res = await fetch(`${API_BASE}/auth/mfa/setup`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

        const data = await res.json();

        if (!res.ok) {
          mostrarMensaje(data.detail || "No se pudo generar el QR.");
          return;
        }

        qrBox.innerHTML = `<img src="${data.qr_base64}" alt="Código QR MFA">`;
        secretBox.textContent = data.secret;
      } catch (error) {
        mostrarMensaje("Error conectando con el backend.");
      }
    }

    document.getElementById("mfaForm").addEventListener("submit", async (e) => {
      e.preventDefault();

      const codigo = document.getElementById("codigo").value.trim();

      try {
        const res = await fetch(`${API_BASE}/auth/mfa/confirm`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify({ codigo })
        });

        const data = await res.json();

        if (!res.ok) {
          mostrarMensaje(data.detail || "Código inválido o expirado.");
          return;
        }

        const usuario = JSON.parse(usuarioRaw || "{}");
        usuario.mfa_totp_enabled = true;
        localStorage.setItem("usuario", JSON.stringify(usuario));
        sessionStorage.removeItem("mfa_config_pendiente");

        mostrarMensaje("MFA configurado correctamente. Redirigiendo...", true);

        setTimeout(() => {
          irDashboardPorRol();
        }, 1000);
      } catch (error) {
        mostrarMensaje("Error confirmando el código MFA.");
      }
    });

    cargarQR();
