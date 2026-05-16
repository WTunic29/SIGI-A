// ─────────────────────────────────────────────
// CONFIG
// ─────────────────────────────────────────────
const API_BASE = "https://sigi-a.onrender.com";
const ROLES = {
  negocio: "Negocio",
  cliente: "Usuario",
  usuario: "Usuario",
  admin: "Administrador",
  empleado: "Empleado",
};

let negociosCache = [];

// ─────────────────────────────────────────────
// NAVBAR
// ─────────────────────────────────────────────
const navbar = document.getElementById("navbar");
window.addEventListener("scroll", () => {
  navbar?.classList.toggle("scrolled", window.scrollY > 60);
});

document.addEventListener("click", (e) => {
  const navUser = document.getElementById("navUser");
  const dropdown = document.getElementById("userDropdown");
  if (navUser && dropdown && !navUser.contains(e.target)) {
    dropdown.classList.remove("show");
  }
});

function toggleUserMenu() {
  document.getElementById("userDropdown")?.classList.toggle("show");
}

function actualizarNavbar() {
  const usuario = getUsuario();
  const navGuest = document.getElementById("navGuest");
  const navUser = document.getElementById("navUser");
  const navUserName = document.getElementById("navUserName");
  const menuRegistrarNegocio = document.getElementById("menuRegistrarNegocio");
  const menuValidarAcceso = document.getElementById("menuValidarAcceso");

  if (!usuario) {
    if (navGuest) navGuest.style.display = "flex";
    if (navUser) navUser.style.display = "none";
    return;
  }

  if (navGuest) navGuest.style.display = "none";
  if (navUser) navUser.style.display = "block";
  if (navUserName) navUserName.textContent = usuario.nombre || usuario.correo || "Usuario";

  const esNegocio = normalizarRol(usuario.rol) === "negocio";
  if (menuRegistrarNegocio) menuRegistrarNegocio.style.display = esNegocio ? "block" : "none";
  if (menuValidarAcceso) menuValidarAcceso.style.display = esNegocio ? "block" : "none";
}

// ─────────────────────────────────────────────
// NAVEGACIÓN ENTRE PANTALLAS
// ─────────────────────────────────────────────
const TODAS = [
  "inicio", "cta", "login", "registro", "verify2fa",
  "dashboard-negocio", "dashboard-usuario", "mi-perfil",
  "ver-negocios", "validar-acceso", "registrar-negocio"
];

function setVisible(show, hide = TODAS) {
  hide.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = "none";
  });
  show.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = "flex";
  });
  actualizarNavbar();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function mostrarInicio() {
  const usuario = getUsuario();
  if (usuario) return irDashboardPorRol();
  setVisible(["inicio", "cta"]);
}

function mostrarLogin() { setVisible(["login"]); }

function mostrarRegistro(rol = null) {
  setVisible(["registro"]);
  if (rol) {
    const input = document.querySelector(`input[name="rolRegistro"][value="${rol}"]`);
    if (input) input.checked = true;
  }
}

function mostrarVerify2FA() { setVisible(["verify2fa"]); }
function mostrarDashboardNegocio() { setVisible(["dashboard-negocio"]); }
function mostrarDashboardUsuario() { setVisible(["dashboard-usuario"]); }
function mostrarMiPerfil() { setVisible(["mi-perfil"]); }
function mostrarVerNegocios() { setVisible(["ver-negocios"]); }
function mostrarValidarAcceso() { setVisible(["validar-acceso"]); }
function mostrarRegistrarNegocio() { setVisible(["registrar-negocio"]); }

function irDashboardPorRol() {
  const usuario = getUsuario();
  if (!usuario) return mostrarInicio();

  if (normalizarRol(usuario.rol) === "negocio") {
    mostrarDashboardNegocio();
    cargarDatosDashboard(usuario);
  } else {
    mostrarDashboardUsuario();
    cargarDatosDashboardUsuario(usuario);
    cargarNegociosUsuario();
  }
}

// ─────────────────────────────────────────────
// UTILIDADES
// ─────────────────────────────────────────────
function mostrarMensaje(containerId, texto, esError = true) {
  const msg = document.getElementById(containerId);
  if (!msg) return;
  msg.textContent = texto;
  msg.className = `form-msg ${esError ? "error" : "success"}`;
  msg.style.display = texto ? "block" : "none";
}

function getToken() {
  return localStorage.getItem("access_token");
}

function getUsuario() {
  try {
    return JSON.parse(localStorage.getItem("usuario") || "null");
  } catch {
    return null;
  }
}

function normalizarRol(rol) {
  if (!rol) return "cliente";
  if (rol === "usuario") return "cliente";
  return rol;
}

function guardarSesion(data) {
  localStorage.setItem("access_token", data.access_token);
  if (data.refresh_token) localStorage.setItem("refresh_token", data.refresh_token);
  localStorage.setItem("usuario", JSON.stringify(data.usuario));
  actualizarNavbar();
}

function cerrarSesion() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("usuario");
  sessionStorage.removeItem("correo_2fa");
  actualizarNavbar();
  setVisible(["inicio", "cta"]);
}

function campoNegocio(n, ...keys) {
  for (const key of keys) {
    if (n && n[key] !== undefined && n[key] !== null && n[key] !== "") return n[key];
  }
  return "";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderNegocios(lista, contenedorId) {
  const contenedor = document.getElementById(contenedorId);
  if (!contenedor) return;

  if (!Array.isArray(lista) || lista.length === 0) {
    contenedor.innerHTML = `<div class="empty-state">No hay negocios registrados todavía.</div>`;
    return;
  }

  contenedor.innerHTML = lista.map(n => {
    const nombre = escapeHtml(campoNegocio(n, "nombre_negocio", "nombre", "name") || "Negocio sin nombre");
    const descripcion = escapeHtml(campoNegocio(n, "descripcion", "description") || "Sin descripción registrada");
    const direccion = escapeHtml(campoNegocio(n, "direccion", "address") || "Sin dirección");
    const telefono = escapeHtml(campoNegocio(n, "telefono", "phone") || "Sin teléfono");
    const correo = escapeHtml(campoNegocio(n, "correo", "email") || "Sin correo");

    return `
      <article class="business-card">
        <div class="business-avatar">${nombre.charAt(0).toUpperCase()}</div>
        <div class="business-content">
          <h3>${nombre}</h3>
          <p>${descripcion}</p>
          <div class="business-meta">
            <span>📍 ${direccion}</span>
            <span>📞 ${telefono}</span>
            <span>✉️ ${correo}</span>
          </div>
        </div>
      </article>
    `;
  }).join("");
}

// ─────────────────────────────────────────────
// FORMULARIOS
// ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  actualizarNavbar();

  document.getElementById("registroForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const rolSeleccionado = document.querySelector('input[name="rolRegistro"]:checked')?.value || "cliente";
    const payload = {
      nombre: document.getElementById("nombre").value.trim(),
      apellido: document.getElementById("apellido").value.trim(),
      correo: document.getElementById("correo").value.trim(),
      telefono: document.getElementById("telefono").value.trim(),
      password: document.getElementById("password").value,
      rol: rolSeleccionado,
    };

    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));

      if (res.status === 201 || res.ok) {
        mostrarMensaje("registroMsg", `Cuenta creada como ${ROLES[rolSeleccionado] || rolSeleccionado}. Ahora inicia sesión.`, false);
        document.getElementById("registroForm").reset();
        setTimeout(mostrarLogin, 1200);
      } else {
        mostrarMensaje("registroMsg", data.detail || "Error al registrarse. Revisa los datos.");
      }
    } catch {
      mostrarMensaje("registroMsg", "No se pudo conectar al servidor.");
    }
  });

  document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      correo: document.getElementById("loginCorreo").value.trim(),
      password: document.getElementById("loginPassword").value,
    };

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));

      if (res.ok && data.requieres_2fa) {
        sessionStorage.setItem("correo_2fa", data.correo || payload.correo);
        mostrarVerify2FA();
        mostrarMensaje("verify2faMsg", "Código enviado a tu correo.", false);
      } else if (res.ok && data.access_token && data.usuario) {
        guardarSesion(data);
        irDashboardPorRol();
      } else {
        mostrarMensaje("loginMsg", data.detail || "Credenciales inválidas.");
      }
    } catch {
      mostrarMensaje("loginMsg", "No se pudo conectar al servidor.");
    }
  });

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
      const data = await res.json().catch(() => ({}));

      if (res.ok && data.access_token && data.usuario) {
        guardarSesion(data);
        sessionStorage.removeItem("correo_2fa");
        irDashboardPorRol();
      } else {
        mostrarMensaje("verify2faMsg", data.detail || "Código inválido o expirado.");
      }
    } catch {
      mostrarMensaje("verify2faMsg", "No se pudo conectar al servidor.");
    }
  });

  document.getElementById("negocioForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const token = getToken();
    if (!token) return mostrarLogin();

    const payload = {
      nombre: document.getElementById("negNombre").value.trim(),
      descripcion: document.getElementById("negDescripcion").value.trim() || null,
      direccion: document.getElementById("negDireccion").value.trim() || null,
      telefono: document.getElementById("negTelefono").value.trim() || null,
      correo: document.getElementById("negCorreo").value.trim() || null,
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
      const data = await res.json().catch(() => ({}));

      if (res.status === 201 || res.ok) {
        mostrarMensaje("negocioMsg", "Negocio registrado correctamente.", false);
        document.getElementById("negocioForm").reset();
        const nombreNegocio = campoNegocio(data.negocio || data, "nombre_negocio", "nombre") || payload.nombre;
        const span = document.getElementById("dashNombreNegocio");
        if (span) span.textContent = nombreNegocio;
      } else if (res.status === 401 || res.status === 403) {
        mostrarMensaje("negocioMsg", "Sesión expirada o sin permisos.");
      } else {
        mostrarMensaje("negocioMsg", data.detail || "Error al crear el negocio.");
      }
    } catch {
      mostrarMensaje("negocioMsg", "No se pudo conectar al servidor.");
    }
  });

  checkSession();
});

// ─────────────────────────────────────────────
// DASHBOARDS
// ─────────────────────────────────────────────
function cargarDatosDashboard(usuario) {
  document.getElementById("dashNombreUsuario").textContent = `${usuario.nombre || ""} ${usuario.apellido || ""}`.trim() || usuario.correo;

  const token = getToken();
  if (!token) return;

  fetch(`${API_BASE}/negocios/`, { headers: { "Authorization": `Bearer ${token}` } })
    .then(res => res.json())
    .then(data => {
      if (!Array.isArray(data)) return;
      const miNegocio = data.find(n =>
        campoNegocio(n, "id_usuario_propietario", "usuario_id", "propietario_id") === usuario.id
      );
      const span = document.getElementById("dashNombreNegocio");
      if (span) span.textContent = miNegocio ? campoNegocio(miNegocio, "nombre_negocio", "nombre") : "Sin negocio aún";
    })
    .catch(() => {});
}

function cargarDatosDashboardUsuario(usuario) {
  const nombre = `${usuario.nombre || ""} ${usuario.apellido || ""}`.trim() || usuario.correo;
  document.getElementById("userDashNombre").textContent = nombre;
}

function checkSession() {
  const usuario = getUsuario();
  if (!getToken() || !usuario) {
    actualizarNavbar();
    return;
  }
  irDashboardPorRol();
}

// ─────────────────────────────────────────────
// BOTONES / API
// ─────────────────────────────────────────────
async function irMiPerfil() {
  const token = getToken();
  if (!token) return mostrarLogin();

  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    const data = await res.json().catch(() => ({}));

    if (res.ok) {
      document.getElementById("perfilNombre").textContent = data.nombre || "—";
      document.getElementById("perfilApellido").textContent = data.apellido || "—";
      document.getElementById("perfilCorreo").textContent = data.correo || "—";
      document.getElementById("perfilRol").textContent = ROLES[normalizarRol(data.rol)] || data.rol || "—";
      mostrarMensaje("perfilMsg", "", false);
    } else {
      mostrarMensaje("perfilMsg", data.detail || "No se pudo cargar el perfil.");
    }
    mostrarMiPerfil();
  } catch {
    mostrarMensaje("perfilMsg", "No se pudo conectar al servidor.");
    mostrarMiPerfil();
  }
}

function irRegistrarNegocio() {
  const usuario = getUsuario();
  if (!usuario) return mostrarLogin();
  if (normalizarRol(usuario.rol) !== "negocio") {
    alert("Solo las cuentas tipo negocio pueden registrar un negocio.");
    return irDashboardPorRol();
  }
  mostrarRegistrarNegocio();
}

async function obtenerNegocios() {
  const token = getToken();
  const headers = token ? { "Authorization": `Bearer ${token}` } : {};
  const res = await fetch(`${API_BASE}/negocios/`, { headers });
  const data = await res.json().catch(() => []);
  if (!res.ok) throw new Error(data.detail || "No se pudieron cargar los negocios.");
  return Array.isArray(data) ? data : [];
}

async function irVerNegocios() {
  try {
    const data = await obtenerNegocios();
    negociosCache = data;
    renderNegocios(data, "listaNegocios");
    mostrarMensaje("verNegociosMsg", "", false);
  } catch (error) {
    renderNegocios([], "listaNegocios");
    mostrarMensaje("verNegociosMsg", error.message || "No se pudo conectar al servidor.");
  }
  mostrarVerNegocios();
}

async function cargarNegociosUsuario() {
  try {
    const data = await obtenerNegocios();
    negociosCache = data;
    renderNegocios(data, "listaNegociosUsuario");
    mostrarMensaje("usuarioNegociosMsg", "", false);
  } catch (error) {
    renderNegocios([], "listaNegociosUsuario");
    mostrarMensaje("usuarioNegociosMsg", error.message || "No se pudo conectar al servidor.");
  }
}

function filtrarNegociosUsuario() {
  const q = document.getElementById("buscarNegocio")?.value.toLowerCase().trim() || "";
  if (!q) return renderNegocios(negociosCache, "listaNegociosUsuario");

  const filtrados = negociosCache.filter(n => {
    const texto = [
      campoNegocio(n, "nombre_negocio", "nombre"),
      campoNegocio(n, "descripcion"),
      campoNegocio(n, "direccion"),
      campoNegocio(n, "telefono"),
      campoNegocio(n, "correo"),
    ].join(" ").toLowerCase();
    return texto.includes(q);
  });

  renderNegocios(filtrados, "listaNegociosUsuario");
}

async function irValidarAcceso() {
  const token = getToken();
  if (!token) return mostrarLogin();

  try {
    const res = await fetch(`${API_BASE}/auth/solo-negocio`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    const data = await res.json().catch(() => ({}));
    const info = document.getElementById("validarInfo");

    if (res.ok) {
      info.innerHTML = `
        <p><span>Estado</span><strong class="ok">Acceso validado</strong></p>
        <p><span>Mensaje</span><strong>${escapeHtml(data.message || "Permiso correcto")}</strong></p>
        <p><span>Usuario</span><strong>${escapeHtml(data.usuario || "—")}</strong></p>
      `;
      mostrarMensaje("validarMsg", "", false);
    } else {
      info.innerHTML = `<p><span>Estado</span><strong class="bad">${escapeHtml(data.detail || "Acceso denegado")}</strong></p>`;
    }
    mostrarValidarAcceso();
  } catch {
    mostrarMensaje("validarMsg", "No se pudo conectar al servidor.");
    mostrarValidarAcceso();
  }
}
