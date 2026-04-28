// ─────────────────────────────────────────────
//  CONFIG
// ─────────────────────────────────────────────
const API_BASE = "http://localhost:8000";

// ─────────────────────────────────────────────
//  NAVBAR SCROLL
// ─────────────────────────────────────────────
const navbar = document.getElementById("navbar");
window.addEventListener("scroll", () => {
  navbar.classList.toggle("scrolled", window.scrollY > 60);
});

// ─────────────────────────────────────────────
//  NAVEGACIÓN ENTRE "PANTALLAS"
// ─────────────────────────────────────────────
function mostrarInicio() {
  setVisible(["inicio", "cta"], ["login", "registro", "verify2fa", "dashboard-negocio"]);
}

function mostrarLogin() {
  setVisible(["login"], ["inicio", "cta", "registro", "verify2fa", "dashboard-negocio"]);
}

function mostrarRegistro() {
  setVisible(["registro"], ["inicio", "cta", "login", "verify2fa", "dashboard-negocio"]);
}

function mostrarVerify2FA() {
  setVisible(["verify2fa"], ["inicio", "cta", "login", "registro", "dashboard-negocio"]);
}

function mostrarDashboardNegocio() {
  setVisible(["dashboard-negocio"], ["inicio", "cta", "login", "registro", "verify2fa"]);
}

/** Muestra los ids en `show` y oculta los de `hide` */
function setVisible(show, hide) {
  show.forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.style.display = "flex";
  });
  hide.forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.style.display = "none";
  });
}

// ─────────────────────────────────────────────
//  UTILIDADES
// ─────────────────────────────────────────────

/** Muestra un mensaje de error/éxito debajo de un formulario */
function mostrarMensaje(containerId, texto, esError = true) {
  let msg = document.getElementById(containerId);
  if (!msg) return;
  msg.textContent = texto;
  msg.style.color = esError ? "#e74c3c" : "#2ecc71";
  msg.style.marginTop = "8px";
  msg.style.display = "block";
}

function getToken() {
  return localStorage.getItem("access_token");
}

// ─────────────────────────────────────────────
//  FORMULARIOS
// ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {

  // ── REGISTRO DE USUARIO (rol: negocio) ──────
  document.getElementById("registroForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      nombre:   document.getElementById("nombre").value.trim(),
      apellido: document.getElementById("apellido").value.trim(),
      correo:   document.getElementById("correo").value.trim(),
      telefono: document.getElementById("telefono").value.trim(),
      password: document.getElementById("password").value,
      rol:      "negocio",           // rol fijo para registro desde el landing
    };

    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.status === 201) {
        mostrarMensaje("registroMsg", "Cuenta creada. Ahora inicia sesión.", false);
        setTimeout(mostrarLogin, 1500);
      } else {
        mostrarMensaje("registroMsg", data.detail || "Error al registrarse.");
      }
    } catch {
      mostrarMensaje("registroMsg", "No se pudo conectar al servidor.");
    }
  });

  // ── LOGIN PASO 1: credenciales ───────────────
  document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      correo:   document.getElementById("loginCorreo").value.trim(),
      password: document.getElementById("loginPassword").value,
    };

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok && data.requieres_2fa) {
        // Guardar el correo para usarlo en el paso 2
        sessionStorage.setItem("correo_2fa", data.correo);
        mostrarVerify2FA();
        mostrarMensaje("verify2faMsg", "📧 Código enviado a tu correo.", false);
      } else {
        mostrarMensaje("loginMsg", data.detail || "Credenciales inválidas.");
      }
    } catch {
      mostrarMensaje("loginMsg", "No se pudo conectar al servidor.");
    }
  });

  // ── LOGIN PASO 2: verificar código 2FA ───────
  document.getElementById("verify2faForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      correo: sessionStorage.getItem("correo_2fa"),
      codigo: document.getElementById("codigo2fa").value.trim(),
    };

    try {
      const res = await fetch(`${API_BASE}/auth/verify-2fa`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok) {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("usuario", JSON.stringify(data.usuario));
        sessionStorage.removeItem("correo_2fa");

        // Si el usuario es de rol "negocio" → panel de negocio
        if (data.usuario.rol === "negocio") {
          mostrarDashboardNegocio();
          cargarDatosDashboard(data.usuario);
        } else {
          mostrarInicio();
        }
      } else {
        mostrarMensaje("verify2faMsg", data.detail || "Código inválido o expirado.");
      }
    } catch {
      mostrarMensaje("verify2faMsg", "No se pudo conectar al servidor.");
    }
  });

  // ── CREAR NEGOCIO ────────────────────────────
  document.getElementById("negocioForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = getToken();
    if (!token) { mostrarLogin(); return; }

    const payload = {
      nombre:      document.getElementById("negNombre").value.trim(),
      descripcion: document.getElementById("negDescripcion").value.trim() || null,
      direccion:   document.getElementById("negDireccion").value.trim() || null,
      telefono:    document.getElementById("negTelefono").value.trim() || null,
      correo:      document.getElementById("negCorreo").value.trim() || null,
    };

    try {
      const res = await fetch(`${API_BASE}/negocios/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.status === 201) {
        mostrarMensaje("negocioMsg", "Negocio registrado correctamente.", false);
        document.getElementById("negocioForm").reset();
        // Actualizar nombre del negocio en el dashboard
        const span = document.getElementById("dashNombreNegocio");
        if (span) span.textContent = data.negocio.nombre;
      } else if (res.status === 400) {
        mostrarMensaje("negocioMsg", data.detail || "Ya tienes un negocio registrado.");
      } else if (res.status === 401 || res.status === 403) {
        mostrarMensaje("negocioMsg", "Sesión expirada. Inicia sesión de nuevo.");
        setTimeout(mostrarLogin, 1500);
      } else {
        mostrarMensaje("negocioMsg", data.detail || "Error al crear el negocio.");
      }
    } catch {
      mostrarMensaje("negocioMsg", "No se pudo conectar al servidor.");
    }
  });

});

// ─────────────────────────────────────────────
//  DASHBOARD DE NEGOCIO
// ─────────────────────────────────────────────
function cargarDatosDashboard(usuario) {
  const el = document.getElementById("dashNombreUsuario");
  if (el) el.textContent = `${usuario.nombre} ${usuario.apellido}`;
}

function cerrarSesion() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("usuario");
  mostrarInicio();
}

// ─────────────────────────────────────────────
//  AUTO-LOGIN: si ya hay token, saltar al dashboard
// ─────────────────────────────────────────────
(function checkSession() {
  const token = getToken();
  const usuario = JSON.parse(localStorage.getItem("usuario") || "null");
  if (token && usuario?.rol === "negocio") {
    mostrarDashboardNegocio();
    cargarDatosDashboard(usuario);
  }
})();
