// ─────────────────────────────────────────────
//  CONFIG
// ─────────────────────────────────────────────
const API_BASE = "https://sigi-a.onrender.com";

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
const TODAS = ["inicio","cta","login","registro","verify2fa","dashboard-negocio","mi-perfil","ver-negocios","validar-acceso","registrar-negocio"];

function mostrarInicio()           { setVisible(["inicio","cta"], TODAS); }
function mostrarLogin()            { setVisible(["login"], TODAS); }
function mostrarRegistro()         { setVisible(["registro"], TODAS); }
function mostrarVerify2FA()        { setVisible(["verify2fa"], TODAS); }
function mostrarDashboardNegocio() { setVisible(["dashboard-negocio"], TODAS); }
function mostrarMiPerfil()         { setVisible(["mi-perfil"], TODAS); }
function mostrarVerNegocios()      { setVisible(["ver-negocios"], TODAS); }
function mostrarValidarAcceso()    { setVisible(["validar-acceso"], TODAS); }
function mostrarRegistrarNegocio() { setVisible(["registrar-negocio"], TODAS); }

function setVisible(show, hide) {
  hide.forEach(id => { const el = document.getElementById(id); if (el) el.style.display = "none"; });
  show.forEach(id => { const el = document.getElementById(id); if (el) el.style.display = "flex"; });
}

// ─────────────────────────────────────────────
//  UTILIDADES
// ─────────────────────────────────────────────
function mostrarMensaje(containerId, texto, esError = true) {
  const msg = document.getElementById(containerId);
  if (!msg) return;
  msg.textContent = texto;
  msg.style.color = esError ? "#e74c3c" : "#2ecc71";
  msg.style.marginTop = "8px";
  msg.style.display = "block";
}

function getToken() { return localStorage.getItem("access_token"); }

const ROLES = { "negocio": "Propietario", "cliente": "Cliente", "admin": "Administrador", "empleado": "Empleado" };

// ─────────────────────────────────────────────
//  FORMULARIOS
// ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {

  // ── REGISTRO ──────────────────────────────
  document.getElementById("registroForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      nombre:   document.getElementById("nombre").value.trim(),
      apellido: document.getElementById("apellido").value.trim(),
      correo:   document.getElementById("correo").value.trim(),
      telefono: document.getElementById("telefono").value.trim(),
      password: document.getElementById("password").value,
      rol:      "negocio",
    };
    try {
      const res  = await fetch(`${API_BASE}/auth/register`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload) });
      const data = await res.json();
      if (res.status === 201) { mostrarMensaje("registroMsg", "Cuenta creada. Ahora inicia sesión.", false); setTimeout(mostrarLogin, 1500); }
      else mostrarMensaje("registroMsg", data.detail || "Error al registrarse.");
    } catch { mostrarMensaje("registroMsg", "No se pudo conectar al servidor."); }
  });

  // ── LOGIN PASO 1 ───────────────────────────
  document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      correo:   document.getElementById("loginCorreo").value.trim(),
      password: document.getElementById("loginPassword").value,
    };
    try {
      const res  = await fetch(`${API_BASE}/auth/login`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload) });
      const data = await res.json();
      if (res.ok && data.requieres_2fa) {
        sessionStorage.setItem("correo_2fa", data.correo);
        mostrarVerify2FA();
        mostrarMensaje("verify2faMsg", "📧 Código enviado a tu correo.", false);
      } else mostrarMensaje("loginMsg", data.detail || "Credenciales inválidas.");
    } catch { mostrarMensaje("loginMsg", "No se pudo conectar al servidor."); }
  });

  // ── LOGIN PASO 2: 2FA ──────────────────────
  document.getElementById("verify2faForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = { correo: sessionStorage.getItem("correo_2fa"), codigo: document.getElementById("codigo2fa").value.trim() };
    try {
      const res  = await fetch(`${API_BASE}/auth/verify-2fa`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload) });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("usuario", JSON.stringify(data.usuario));
        sessionStorage.removeItem("correo_2fa");
        if (data.usuario.rol === "negocio") { mostrarDashboardNegocio(); cargarDatosDashboard(data.usuario); }
        else mostrarInicio();
      } else mostrarMensaje("verify2faMsg", data.detail || "Código inválido o expirado.");
    } catch { mostrarMensaje("verify2faMsg", "No se pudo conectar al servidor."); }
  });

  // ── CREAR NEGOCIO ──────────────────────────
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
      const res  = await fetch(`${API_BASE}/negocios/`, { method:"POST", headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`}, body:JSON.stringify(payload) });
      const data = await res.json();
      if (res.status === 201) {
        mostrarMensaje("negocioMsg", "Negocio registrado correctamente.", false);
        document.getElementById("negocioForm").reset();
        const span = document.getElementById("dashNombreNegocio");
        if (span) span.textContent = data.negocio.nombre;
      } else if (res.status === 400) mostrarMensaje("negocioMsg", data.detail || "Ya tienes un negocio registrado.");
      else if (res.status === 401 || res.status === 403) { mostrarMensaje("negocioMsg", "Sesión expirada."); setTimeout(mostrarLogin, 1500); }
      else mostrarMensaje("negocioMsg", data.detail || "Error al crear el negocio.");
    } catch { mostrarMensaje("negocioMsg", "No se pudo conectar al servidor."); }
  });

});

// ─────────────────────────────────────────────
//  DASHBOARD
// ─────────────────────────────────────────────
function cargarDatosDashboard(usuario) {
  const el = document.getElementById("dashNombreUsuario");
  if (el) el.textContent = `${usuario.nombre} ${usuario.apellido}`;

  // Buscar nombre del negocio del usuario
  const token = getToken();
  if (!token) return;
  fetch(`${API_BASE}/negocios/`, { headers: { "Authorization": `Bearer ${token}` } })
    .then(res => res.json())
    .then(data => {
      const miNegocio = data.find(n => n.id_usuario_propietario === usuario.id);
      const span = document.getElementById("dashNombreNegocio");
      if (span) span.textContent = miNegocio ? miNegocio.nombre_negocio : "Sin negocio aún";
    })
    .catch(() => {});
}

function cerrarSesion() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("usuario");
  mostrarInicio();
}

// ─────────────────────────────────────────────
//  AUTO-LOGIN
// ─────────────────────────────────────────────
(function checkSession() {
  const token   = getToken();
  const usuario = JSON.parse(localStorage.getItem("usuario") || "null");
  if (token && usuario?.rol === "negocio") { mostrarDashboardNegocio(); cargarDatosDashboard(usuario); }
})();

// ─────────────────────────────────────────────
//  BOTONES DEL DASHBOARD
// ─────────────────────────────────────────────

// MI PERFIL → GET /auth/me
async function irMiPerfil() {
  const token = getToken();
  if (!token) { mostrarLogin(); return; }
  try {
    const res  = await fetch(`${API_BASE}/auth/me`, { headers: { "Authorization": `Bearer ${token}` } });
    const data = await res.json();
    if (res.ok) {
      document.getElementById("perfilNombre").textContent   = data.nombre;
      document.getElementById("perfilApellido").textContent = data.apellido;
      document.getElementById("perfilCorreo").textContent   = data.correo;
      document.getElementById("perfilRol").textContent      = ROLES[data.rol] || data.rol;
    } else mostrarMensaje("perfilMsg", data.detail || "No se pudo cargar el perfil.");
    mostrarMiPerfil();
  } catch { mostrarMensaje("perfilMsg", "No se pudo conectar al servidor."); mostrarMiPerfil(); }
}

// REGISTRAR NEGOCIO
function irRegistrarNegocio() { mostrarRegistrarNegocio(); }

// VER NEGOCIOS → GET /negocios/
async function irVerNegocios() {
  try {
    const res  = await fetch(`${API_BASE}/negocios/`);
    const data = await res.json();
    const contenedor = document.getElementById("listaNegocios");
    if (!data.length) {
      contenedor.innerHTML = "<p style='color:var(--gray)'>No hay negocios registrados aún.</p>";
    } else {
      contenedor.innerHTML = data.map(n => `
        <div style="border:1px solid rgba(201,168,76,0.3);padding:16px;margin-bottom:12px;border-radius:4px;">
          <p style="color:var(--gold);font-weight:600;font-size:16px;">${n.nombre_negocio}</p>
          <p style="font-size:13px;color:var(--white2);margin-top:4px;">${n.descripcion || "Sin descripción"}</p>
          <p style="font-size:12px;color:var(--gray);margin-top:4px;">📍 ${n.direccion || "Sin dirección"}</p>
          <p style="font-size:12px;color:var(--gray);">📞 ${n.telefono || "Sin teléfono"}</p>
        </div>`).join("");
    }
    mostrarVerNegocios();
  } catch { mostrarMensaje("verNegociosMsg", "No se pudo conectar al servidor."); mostrarVerNegocios(); }
}

// VALIDAR ACCESO NEGOCIO → GET /auth/solo-negocio
async function irValidarAcceso() {
  const token = getToken();
  if (!token) { mostrarLogin(); return; }
  try {
    const res  = await fetch(`${API_BASE}/auth/solo-negocio`, { headers: { "Authorization": `Bearer ${token}` } });
    const data = await res.json();
    const info = document.getElementById("validarInfo");
    if (res.ok) {
      info.innerHTML = `
        <p style="color:#2ecc71;font-size:16px;">✅ Acceso validado correctamente</p>
        <p style="margin-top:12px;">${data.message}</p>
        <p style="color:var(--gold);margin-top:8px;">Usuario: ${data.usuario}</p>`;
    } else {
      info.innerHTML = `<p style="color:#e74c3c;">❌ ${data.detail || "Acceso denegado"}</p>`;
    }
    mostrarValidarAcceso();
  } catch { mostrarMensaje("validarMsg", "No se pudo conectar al servidor."); mostrarValidarAcceso(); }
}