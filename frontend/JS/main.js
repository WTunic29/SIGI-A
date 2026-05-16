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
  const menuNegocioItems = document.querySelectorAll(".menu-negocio");

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
  menuNegocioItems.forEach(item => item.style.display = esNegocio ? "block" : "none");
}

// ─────────────────────────────────────────────
// NAVEGACIÓN ENTRE PANTALLAS
// ─────────────────────────────────────────────
const TODAS = [
  "inicio", "cta", "login", "registro", "verify2fa",
  "dashboard-negocio", "dashboard-usuario", "mi-perfil",
  "ver-negocios", "validar-acceso", "registrar-negocio",
  "gestion-empleados", "gestion-servicios", "gestion-productos", "gestion-citas"
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
        Number(campoNegocio(n, "id_usuario_propietario", "usuario_id", "propietario_id")) === Number(usuario.id_usuario || usuario.id)
      ) || data[0];
      miNegocioCache = miNegocio || null;
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

// ─────────────────────────────────────────────
// MÓDULOS NEGOCIO: EMPLEADOS / SERVICIOS / INVENTARIO / CITAS
// ─────────────────────────────────────────────
let miNegocioCache = null;
const API_PATHS = {
  empleados: "/empleados/",
  servicios: "/servicios/",
  productos: "/productos/",
  citas: "/citas/",
  inventario: "/inventario-movimientos/",
};

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Error ${res.status}`);
  return data;
}

function asegurarRolNegocio() {
  const usuario = getUsuario();
  if (!usuario || !getToken()) { mostrarLogin(); return false; }
  if (normalizarRol(usuario.rol) !== "negocio" && normalizarRol(usuario.rol) !== "admin") {
    alert("Esta opción es solo para cuentas tipo negocio.");
    irDashboardPorRol();
    return false;
  }
  return true;
}

async function obtenerMiNegocio(force = false) {
  if (miNegocioCache && !force) return miNegocioCache;
  const usuario = getUsuario();
  const negocios = await apiFetch("/negocios/");
  miNegocioCache = Array.isArray(negocios)
    ? negocios.find(n => Number(campoNegocio(n, "id_usuario_propietario", "usuario_id", "propietario_id")) === Number(usuario?.id_usuario || usuario?.id)) || negocios[0]
    : null;
  return miNegocioCache;
}

function renderAdminList(items, contenedorId, tipo) {
  const cont = document.getElementById(contenedorId);
  if (!cont) return;
  if (!Array.isArray(items) || items.length === 0) {
    cont.innerHTML = `<div class="empty-state">No hay registros todavía.</div>`;
    return;
  }
  cont.innerHTML = items.map(item => {
    const id = item.id_empleado || item.id_servicio || item.id_producto || item.id_cita;
    const nombre = escapeHtml(item.nombre || item.nombre_negocio || `Registro #${id}`);
    let meta = "";
    let acciones = "";

    if (tipo === "empleado") {
      meta = `${escapeHtml(item.apellido || "")} · ${escapeHtml(item.especialidad || "Sin especialidad")} · ${escapeHtml(item.estado || "")}`;
      acciones = `<button onclick="editarEmpleado(${id})">Editar</button><button onclick="eliminarEmpleado(${id})">Desactivar</button>`;
    }
    if (tipo === "servicio") {
      meta = `${escapeHtml(item.duracion_minutos || "—")} min · $${escapeHtml(item.precio || 0)} · ${escapeHtml(item.estado || "")}`;
      acciones = `<button onclick="editarServicio(${id})">Editar</button><button onclick="eliminarServicio(${id})">Eliminar</button>`;
    }
    if (tipo === "producto") {
      meta = `Stock: ${escapeHtml(item.stock ?? 0)} · $${escapeHtml(item.precio || 0)} · ${escapeHtml(item.estado || "")}`;
      acciones = `<button onclick="editarProducto(${id})">Editar</button><button onclick="movimientoInventario(${id})">Movimiento</button><button onclick="eliminarProducto(${id})">Desactivar</button>`;
    }
    if (tipo === "cita") {
      meta = `Cliente #${escapeHtml(item.id_cliente)} · Empleado #${escapeHtml(item.id_empleado)} · ${escapeHtml(item.fecha)} ${escapeHtml(item.hora_inicio)}-${escapeHtml(item.hora_fin)} · ${escapeHtml(item.estado)}`;
      acciones = `<button onclick="cancelarCita(${id})">Cancelar</button>`;
    }

    return `<article class="admin-item"><div><h4>${nombre}</h4><p>${meta}</p></div><div class="row-actions">${acciones}</div></article>`;
  }).join("");
}

function mostrarGestion(id) {
  if (!asegurarRolNegocio()) return;
  setVisible([id]);
}

async function irGestionEmpleados() { mostrarGestion("gestion-empleados"); await cargarEmpleados(); }
async function irGestionServicios() { mostrarGestion("gestion-servicios"); await cargarServicios(); }
async function irGestionProductos() { mostrarGestion("gestion-productos"); await cargarProductos(); }
async function irGestionCitas() { mostrarGestion("gestion-citas"); await cargarCitas(); }

async function cargarEmpleados() {
  try { renderAdminList(await apiFetch(API_PATHS.empleados), "listaEmpleados", "empleado"); mostrarMensaje("empleadoMsg", "", false); }
  catch (e) { document.getElementById("listaEmpleados").innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`; }
}
async function cargarServicios() {
  try { renderAdminList(await apiFetch(API_PATHS.servicios), "listaServicios", "servicio"); mostrarMensaje("servicioMsg", "", false); }
  catch (e) { document.getElementById("listaServicios").innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`; }
}
async function cargarProductos() {
  try { renderAdminList(await apiFetch(API_PATHS.productos), "listaProductos", "producto"); mostrarMensaje("productoMsg", "", false); }
  catch (e) { document.getElementById("listaProductos").innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`; }
}
async function cargarCitas() {
  try {
    const negocio = await obtenerMiNegocio(true);
    if (!negocio?.id_negocio) throw new Error("Primero debes tener un negocio registrado.");
    renderAdminList(await apiFetch(`${API_PATHS.citas}negocio/${negocio.id_negocio}`), "listaCitas", "cita");
    mostrarMensaje("citasMsg", "", false);
  } catch (e) {
    document.getElementById("listaCitas").innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("empleadoForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      nombre: document.getElementById("empNombre").value.trim(),
      apellido: document.getElementById("empApellido").value.trim(),
      telefono: document.getElementById("empTelefono").value.trim() || null,
      email: document.getElementById("empEmail").value.trim() || null,
      especialidad: document.getElementById("empEspecialidad").value.trim() || null,
      foto_url: document.getElementById("empFoto").value.trim() || null,
    };
    try { await apiFetch(API_PATHS.empleados, { method: "POST", body: JSON.stringify(payload) }); e.target.reset(); mostrarMensaje("empleadoMsg", "Empleado creado correctamente.", false); cargarEmpleados(); }
    catch (err) { mostrarMensaje("empleadoMsg", err.message); }
  });

  document.getElementById("servicioForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      nombre: document.getElementById("serNombre").value.trim(),
      descripcion: document.getElementById("serDescripcion").value.trim() || null,
      duracion_minutos: Number(document.getElementById("serDuracion").value),
      precio: Number(document.getElementById("serPrecio").value),
      imagen_url: document.getElementById("serImagen").value.trim() || null,
    };
    try { await apiFetch(API_PATHS.servicios, { method: "POST", body: JSON.stringify(payload) }); e.target.reset(); mostrarMensaje("servicioMsg", "Servicio creado correctamente.", false); cargarServicios(); }
    catch (err) { mostrarMensaje("servicioMsg", err.message); }
  });

  document.getElementById("productoForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      nombre: document.getElementById("proNombre").value.trim(),
      descripcion: document.getElementById("proDescripcion").value.trim() || null,
      precio: Number(document.getElementById("proPrecio").value),
      stock: Number(document.getElementById("proStock").value),
      imagen_url: document.getElementById("proImagen").value.trim() || null,
    };
    try { await apiFetch(API_PATHS.productos, { method: "POST", body: JSON.stringify(payload) }); e.target.reset(); mostrarMensaje("productoMsg", "Producto creado correctamente.", false); cargarProductos(); }
    catch (err) { mostrarMensaje("productoMsg", err.message); }
  });
});

async function editarEmpleado(id) {
  const especialidad = prompt("Nueva especialidad del empleado:");
  if (especialidad === null) return;
  try { await apiFetch(`${API_PATHS.empleados}${id}`, { method: "PUT", body: JSON.stringify({ especialidad }) }); cargarEmpleados(); }
  catch (e) { alert(e.message); }
}
async function eliminarEmpleado(id) {
  if (!confirm("¿Desactivar este empleado?")) return;
  try { await apiFetch(`${API_PATHS.empleados}${id}`, { method: "DELETE" }); cargarEmpleados(); }
  catch (e) { alert(e.message); }
}
async function editarServicio(id) {
  const precio = prompt("Nuevo precio del servicio:");
  if (precio === null) return;
  try { await apiFetch(`${API_PATHS.servicios}${id}`, { method: "PUT", body: JSON.stringify({ precio: Number(precio) }) }); cargarServicios(); }
  catch (e) { alert(e.message); }
}
async function eliminarServicio(id) {
  if (!confirm("¿Eliminar/desactivar este servicio?")) return;
  try { await apiFetch(`${API_PATHS.servicios}${id}`, { method: "DELETE" }); cargarServicios(); }
  catch (e) { alert(e.message); }
}
async function editarProducto(id) {
  const precio = prompt("Nuevo precio del producto:");
  if (precio === null) return;
  try { await apiFetch(`${API_PATHS.productos}${id}`, { method: "PUT", body: JSON.stringify({ precio: Number(precio) }) }); cargarProductos(); }
  catch (e) { alert(e.message); }
}
async function eliminarProducto(id) {
  if (!confirm("¿Desactivar este producto?")) return;
  try { await apiFetch(`${API_PATHS.productos}${id}`, { method: "DELETE" }); cargarProductos(); }
  catch (e) { alert(e.message); }
}
async function movimientoInventario(id) {
  const tipo_movimiento = prompt("Tipo de movimiento: entrada o salida", "entrada");
  if (!tipo_movimiento) return;
  const cantidad = prompt("Cantidad:", "1");
  if (!cantidad) return;
  const motivo = prompt("Motivo:", "Ajuste manual") || "Ajuste manual";
  try {
    await apiFetch(API_PATHS.inventario, { method: "POST", body: JSON.stringify({ id_producto: id, tipo_movimiento, cantidad: Number(cantidad), motivo }) });
    cargarProductos();
  } catch (e) { alert(e.message); }
}
async function cancelarCita(id) {
  if (!confirm("¿Cancelar esta cita?")) return;
  try { await apiFetch(`${API_PATHS.citas}${id}`, { method: "DELETE" }); cargarCitas(); }
  catch (e) { alert(e.message); }
}
