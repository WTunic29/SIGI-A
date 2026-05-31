// ─────────────────────────────────────────────
// CONFIG
// ─────────────────────────────────────────────
const API_BASE = window.SIGIA_API_BASE || "http://3.15.197.152:10000";
const ROLES = {
  negocio: "Negocio",
  cliente: "Usuario",
  usuario: "Usuario",
  admin: "Administrador",
  administrador: "Administrador",
  superusuario: "Superusuario",
  superuser: "Superusuario",
  empleado: "Empleado",
};

let negociosCache = [];
let empleadosCache = [];
let loginVerificationMode = "email";

function obtenerMensajeError(error) {
  if (!error) return "Ocurrió un error inesperado.";

  if (typeof error === "string") {
    return error;
  }

  if (error.detail) {
    if (Array.isArray(error.detail)) {
      return error.detail.map(e => e.msg || JSON.stringify(e)).join(" | ");
    }

    return error.detail;
  }

  if (error.message) {
    return error.message;
  }

  return "Ocurrió un error inesperado.";
}

async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  let data = null;

  try {
    data = await response.json();
  } catch (e) {
    data = null;
  }

  if (!response.ok) {
    throw data || {
      detail: `Error HTTP ${response.status}`
    };
  }

  return data;
}

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
  const menuClienteItems = document.querySelectorAll(".menu-cliente");

  if (!usuario) {
    if (navGuest) navGuest.style.display = "flex";
    if (navUser) navUser.style.display = "none";
    return;
  }

  if (navGuest) navGuest.style.display = "none";
  if (navUser) navUser.style.display = "block";
  if (navUserName) navUserName.textContent = usuario.nombre || usuario.correo || "Usuario";

  const rolActual = normalizarRol(usuario.rol);
  const esAdmin = rolActual === "admin";
  const esNegocio = rolActual === "negocio" || esAdmin;
  const esCliente = rolActual === "cliente" || esAdmin;
  if (menuRegistrarNegocio) menuRegistrarNegocio.style.display = (rolActual === "negocio") ? "block" : "none";
  if (menuValidarAcceso) menuValidarAcceso.style.display = esNegocio ? "block" : "none";
  menuNegocioItems.forEach(item => item.style.display = esNegocio ? "block" : "none");
  menuClienteItems.forEach(item => item.style.display = esCliente ? "block" : "none");
}

// ─────────────────────────────────────────────
// NAVEGACIÓN ENTRE PANTALLAS
// ─────────────────────────────────────────────
const TODAS = [
  "inicio", "cta", "login", "registro", "recuperar-password", "verify2fa",
  "dashboard-negocio", "dashboard-usuario", "dashboard-admin", "gestion-usuarios-admin", "auditoria-admin", "mi-perfil",
  "ver-negocios", "validar-acceso", "registrar-negocio",
  "gestion-empleados", "gestion-servicios", "gestion-productos", "gestion-citas", "detalle-negocio",
  "mis-citas-usuario", "mis-calificaciones-usuario", "tienda-usuario", "carrito-usuario", "mis-pedidos-usuario"
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

function mostrarRecuperarPassword() {
  setVisible(["recuperar-password"]);
  mostrarMensaje("forgotPasswordMsg", "", false);
  setTimeout(() => document.getElementById("forgotCorreo")?.focus(), 150);
}

function mostrarRegistro(rol = null) {
  setVisible(["registro"]);
  if (rol) {
    const input = document.querySelector(`input[name="rolRegistro"][value="${rol}"]`);
    if (input) input.checked = true;
  }
}

function togglePasswordVisibility(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;

  const visible = input.type === "text";
  input.type = visible ? "password" : "text";

  if (btn) {
    btn.textContent = visible ? "Ver" : "Ocultar";
    btn.setAttribute("aria-label", visible ? "Mostrar contraseña" : "Ocultar contraseña");
  }
}

function configurarPantallaVerificacion(tipo = "email") {
  loginVerificationMode = tipo === "totp" ? "totp" : "email";
  sessionStorage.setItem("mfa_mode", loginVerificationMode);

  const title = document.getElementById("verify2faTitle");
  const text = document.getElementById("verify2faText");
  const input = document.getElementById("codigo2fa");
  const btn = document.getElementById("verify2faBtn");

  if (loginVerificationMode === "totp") {
    if (title) title.innerHTML = "Verificación con <span>App</span>";
    if (text) text.textContent = "Ingresa el código de 6 dígitos generado por Google Authenticator o Microsoft Authenticator.";
    if (input) input.placeholder = "Código de 6 dígitos";
    if (btn) btn.textContent = "Verificar";
  } else {
    if (title) title.innerHTML = "Verificar <span>Código</span>";
    if (text) text.textContent = "Ingresa el código de 6 dígitos que enviamos a tu correo.";
    if (input) input.placeholder = "Código MFA";
    if (btn) btn.textContent = "Verificar";
  }
}

function mostrarVerifyMFA(tipo = "email") {
  configurarPantallaVerificacion(tipo);
  setVisible(["verify2fa"]);
  setTimeout(() => document.getElementById("codigo2fa")?.focus(), 150);
}
function mostrarDashboardNegocio() { setVisible(["dashboard-negocio"]); }
function mostrarDashboardUsuario() { setVisible(["dashboard-usuario"]); }
function mostrarDashboardAdmin() { setVisible(["dashboard-admin"]); }
function mostrarMiPerfil() { setVisible(["mi-perfil"]); }
function mostrarVerNegocios() { setVisible(["ver-negocios"]); }
function mostrarValidarAcceso() { setVisible(["validar-acceso"]); }
function mostrarRegistrarNegocio() { setVisible(["registrar-negocio"]); }
function mostrarDetalleNegocio() { setVisible(["detalle-negocio"]); }

function paginaActual() {
  return (window.location.pathname.split("/").pop() || "index.html").toLowerCase();
}

function rutaDashboardPorRol(rol) {
  const normalizado = normalizarRol(rol);
  if (normalizado === "admin") return "superusuario.html";
  if (normalizado === "negocio") return "negocio.html";
  return "usuario.html";
}

function esPaginaDashboardRol(pagina = paginaActual()) {
  return ["usuario.html", "negocio.html", "superusuario.html"].includes(pagina);
}

function irDashboardPorRol() {
  const usuario = getUsuario();
  if (!usuario) {
    window.location.href = "login.html";
    return;
  }

  const rol = normalizarRol(usuario.rol);
  const destino = rutaDashboardPorRol(rol);
  const pagina = paginaActual();

  if (!esPaginaDashboardRol(pagina) || pagina !== destino) {
    window.location.href = destino;
    return;
  }

  if (rol === "admin") {
    mostrarDashboardAdmin();
    cargarDatosDashboardAdmin(usuario);
  } else if (rol === "negocio") {
    mostrarDashboardNegocio();
    cargarDatosDashboard(usuario);
  } else {
    mostrarDashboardUsuario();
    cargarDatosDashboardUsuario(usuario);
    cargarNegociosUsuario();
  }
  finalizarCargaDashboard();
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

function normalizarTextoError(input) {
  if (!input) return "";

  if (typeof input === "string") {
    return input === "[object Object]" ? "" : input;
  }

  if (input instanceof Error) {
    return input.message === "[object Object]" ? "" : input.message;
  }

  const detail = input.detail ?? input.message ?? input.error ?? input.errors ?? input;

  if (typeof detail === "string") {
    return detail === "[object Object]" ? "" : detail;
  }

  if (Array.isArray(detail)) {
    return detail.map((err) => {
      const campo = Array.isArray(err?.loc) ? String(err.loc[err.loc.length - 1]) : String(err?.field || "campo");
      const mensaje = err?.msg || err?.message || err?.type || JSON.stringify(err);
      return `${campo}: ${mensaje}`;
    }).join(" | ");
  }

  if (typeof detail === "object") {
    const posible = detail.msg || detail.message || detail.detail || detail.error;
    if (posible) return normalizarTextoError(posible);
    try {
      return JSON.stringify(detail);
    } catch {
      return "";
    }
  }

  return String(detail || "");
}

function esErrorPassword(texto) {
  const msg = String(texto || "").toLowerCase();
  return msg.includes("password") ||
    msg.includes("contraseña") ||
    msg.includes("contrasena") ||
    msg.includes("too short") ||
    msg.includes("too_short") ||
    msg.includes("min_length") ||
    msg.includes("at least") ||
    msg.includes("mínimo") ||
    msg.includes("minimo") ||
    msg.includes("uppercase") ||
    msg.includes("lowercase") ||
    msg.includes("special") ||
    msg.includes("digit") ||
    msg.includes("number");
}

function mensajePoliticaPassword() {
  return "La contraseña no cumple los requisitos. Usa mínimo 8 caracteres, una mayúscula, una minúscula, un número y un símbolo.";
}

function validarPasswordFuerte(password) {
  const pass = String(password || "");
  return pass.length >= 8 &&
    /[A-ZÁÉÍÓÚÑ]/.test(pass) &&
    /[a-záéíóúñ]/.test(pass) &&
    /[0-9]/.test(pass) &&
    /[^A-Za-zÁÉÍÓÚÑáéíóúñ0-9]/.test(pass);
}

function friendlyError(input) {
  const raw = normalizarTextoError(input);
  const msg = String(raw || "").toLowerCase();

  if (esErrorPassword(raw)) {
    return mensajePoliticaPassword();
  }
  if (msg.includes("credenciales") || msg.includes("invalid credentials") || msg.includes("incorrect")) {
    return "El correo o la contraseña no son correctos. Verifica tus datos e intenta nuevamente.";
  }
  if (msg.includes("correo ya") || msg.includes("already registered") || msg.includes("ya está registrado") || msg.includes("ya esta registrado")) {
    return "Este correo ya está registrado. Inicia sesión o usa otro correo.";
  }
  if (msg.includes("email") || msg.includes("correo") || msg.includes("value is not a valid email")) {
    return "Ingresa un correo electrónico válido.";
  }
  if (msg.includes("cuenta") && (msg.includes("activa") || msg.includes("activar") || msg.includes("inactive"))) {
    return "Tu cuenta aún no está activa. Revisa tu correo y activa la cuenta antes de iniciar sesión.";
  }
  if (msg.includes("código") || msg.includes("codigo") || msg.includes("2fa") || msg.includes("mfa") || msg.includes("totp")) {
    if (msg.includes("expir")) return "El código de seguridad venció. Inicia sesión nuevamente para recibir o generar un nuevo código.";
    if (msg.includes("bloque")) return "El código fue bloqueado por varios intentos incorrectos. Inicia sesión nuevamente y solicita un nuevo código.";
    if (msg.includes("configur")) return "La app autenticadora todavía no está configurada para esta cuenta.";
    if (msg.includes("invál") || msg.includes("inval") || msg.includes("incorrect")) return "El código ingresado no es válido. Revisa los 6 dígitos e inténtalo nuevamente.";
    return "No pudimos validar el código de seguridad. Revisa los 6 dígitos e inténtalo nuevamente.";
  }
  if (msg.includes("no autorizado") || msg.includes("unauthorized") || msg.includes("not authenticated") || msg.includes("401")) {
    return "Tu sesión expiró o no tienes autorización. Inicia sesión nuevamente.";
  }
  if (msg.includes("forbidden") || msg.includes("403") || msg.includes("permiso")) {
    return "No tienes permisos para realizar esta acción.";
  }
  if (msg.includes("token") && (msg.includes("expir") || msg.includes("venc"))) {
    return "El enlace para restablecer la contraseña venció. Solicita uno nuevo desde Olvidé mi contraseña.";
  }
  if (msg.includes("token") && (msg.includes("invalid") || msg.includes("invál") || msg.includes("inval"))) {
    return "El enlace para restablecer la contraseña no es válido. Solicita uno nuevo desde Olvidé mi contraseña.";
  }
  if (msg.includes("not found") || msg.includes("404")) {
    return "No encontramos la información solicitada. Actualiza la pantalla e intenta de nuevo.";
  }
  if (msg.includes("failed to fetch") || msg.includes("conectar") || msg.includes("network")) {
    return "No se pudo conectar con el servidor. Espera unos segundos e intenta nuevamente.";
  }
  if (raw) return raw.replace(/^\[\d+\]\s*[^:]+:\s*/, "");
  return "Ocurrió un error inesperado. Intenta nuevamente.";
}

function showToast(message, type = "info", duration = 4200) {
  const container = document.getElementById("toastContainer");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  const icon = type === "success" ? "✓" : type === "error" ? "!" : "i";
  toast.innerHTML = `<span class="toast-icon">${icon}</span><p>${escapeHtml(message)}</p><button type="button" aria-label="Cerrar">×</button>`;
  container.appendChild(toast);
  const close = () => {
    toast.classList.add("hide");
    setTimeout(() => toast.remove(), 220);
  };
  toast.querySelector("button")?.addEventListener("click", close);
  setTimeout(close, duration);
}


function closeUiModal(result = null) {
  const modal = document.getElementById("uiModalRoot");
  if (!modal) return;
  modal.classList.remove("show");
  modal.style.display = "none";
  modal.setAttribute("aria-hidden", "true");
  modal.innerHTML = "";
  if (typeof modal._resolver === "function") {
    const resolve = modal._resolver;
    modal._resolver = null;
    resolve(result);
  }
}

function openUiModal({ eyebrow = "SIGI-E", title = "Confirmación", text = "", fields = [], confirmText = "Aceptar", cancelText = "Cancelar", showCancel = true, danger = false } = {}) {
  const modal = document.getElementById("uiModalRoot");
  if (!modal) {
    showToast("No se pudo abrir la ventana de confirmación.", "error");
    return Promise.resolve(null);
  }

  const fieldsHtml = fields.map((field) => {
    const id = escapeHtml(field.id);
    const label = escapeHtml(field.label || "Campo");
    const placeholder = escapeHtml(field.placeholder || "");
    const value = escapeHtml(field.value ?? "");
    const min = field.min !== undefined ? ` min="${escapeHtml(field.min)}"` : "";
    const max = field.max !== undefined ? ` max="${escapeHtml(field.max)}"` : "";
    const step = field.step !== undefined ? ` step="${escapeHtml(field.step)}"` : "";
    const required = field.required === false ? "" : " required";

    if (field.type === "textarea") {
      return `<div class="ui-modal-field"><label for="${id}">${label}</label><textarea id="${id}" placeholder="${placeholder}"${required}>${value}</textarea></div>`;
    }

    if (field.type === "select") {
      const options = (field.options || []).map(opt => `<option value="${escapeHtml(opt.value)}" ${String(opt.value) === String(field.value ?? "") ? "selected" : ""}>${escapeHtml(opt.label)}</option>`).join("");
      return `<div class="ui-modal-field"><label for="${id}">${label}</label><select id="${id}"${required}>${options}</select></div>`;
    }

    return `<div class="ui-modal-field"><label for="${id}">${label}</label><input id="${id}" type="${escapeHtml(field.type || "text")}" placeholder="${placeholder}" value="${value}"${min}${max}${step}${required}></div>`;
  }).join("");

  modal.innerHTML = `
    <div class="ui-modal-card" role="dialog" aria-modal="true" aria-labelledby="uiModalTitle">
      <div class="ui-modal-eyebrow">${escapeHtml(eyebrow)}</div>
      <h2 class="ui-modal-title" id="uiModalTitle">${escapeHtml(title)}</h2>
      ${text ? `<p class="ui-modal-text">${escapeHtml(text)}</p>` : ""}
      ${fieldsHtml ? `<div class="ui-modal-fields">${fieldsHtml}</div>` : ""}
      <div class="ui-modal-actions">
        ${showCancel ? `<button type="button" class="btn-secondary clean" id="uiModalCancel">${escapeHtml(cancelText)}</button>` : ""}
        <button type="button" class="btn-primary" id="uiModalConfirm">${escapeHtml(confirmText)}</button>
      </div>
    </div>
  `;
  modal.style.display = "flex";
  modal.classList.add("show");
  modal.setAttribute("aria-hidden", "false");

  return new Promise((resolve) => {
    modal._resolver = resolve;
    const closeCancel = () => closeUiModal(null);
    document.getElementById("uiModalCancel")?.addEventListener("click", closeCancel);
    modal.addEventListener("click", (event) => {
      if (event.target === modal) closeCancel();
    }, { once: true });

    document.getElementById("uiModalConfirm")?.addEventListener("click", () => {
      const values = {};
      for (const field of fields) {
        const input = document.getElementById(field.id);
        const rawValue = input?.value ?? "";
        if (field.required !== false && !String(rawValue).trim()) {
          showToast(`Completa el campo: ${field.label || field.id}.`, "error");
          input?.focus();
          return;
        }
        values[field.id] = field.type === "number" ? Number(rawValue) : rawValue;
      }
      closeUiModal(fields.length ? values : true);
    });

    setTimeout(() => {
      const first = modal.querySelector("input, select, textarea, button#uiModalConfirm");
      first?.focus();
    }, 80);
  });
}

async function pedirConfirmacion({ title = "¿Confirmas esta acción?", text = "", confirmText = "Aceptar", cancelText = "Cancelar", danger = false } = {}) {
  return Boolean(await openUiModal({ eyebrow: danger ? "Acción importante" : "Confirmación", title, text, confirmText, cancelText, showCancel: true, danger }));
}

async function pedirCantidadProducto(producto) {
  const stock = Number(producto?.stock ?? 0);
  const result = await openUiModal({
    eyebrow: "Tienda",
    title: "Cantidad del producto",
    text: `Selecciona cuántas unidades quieres pedir de ${producto?.nombre || "este producto"}.`,
    confirmText: "Crear pedido",
    fields: [{ id: "cantidad", label: "Cantidad", type: "number", min: 1, max: stock > 0 ? stock : undefined, step: 1, value: 1, placeholder: "Ej: 1" }]
  });
  if (!result) return null;
  const cantidad = Number(result.cantidad);
  if (!Number.isInteger(cantidad) || cantidad < 1) {
    showToast("Ingresa una cantidad válida mayor a cero.", "error");
    return null;
  }
  if (stock > 0 && cantidad > stock) {
    showToast(`Solo hay ${stock} unidades disponibles.`, "error");
    return null;
  }
  return cantidad;
}

async function pedirPrecioNuevo(titulo, precioActual = "") {
  const result = await openUiModal({
    eyebrow: "Gestión",
    title: titulo,
    text: "Ingresa el nuevo precio. Usa solo números, sin puntos ni comas.",
    confirmText: "Guardar precio",
    fields: [{ id: "precio", label: "Nuevo precio", type: "number", min: 0, step: 100, value: precioActual || "", placeholder: "Ej: 25000" }]
  });
  if (!result) return null;
  const precio = Number(result.precio);
  if (!Number.isFinite(precio) || precio < 0) {
    showToast("Ingresa un precio válido.", "error");
    return null;
  }
  return precio;
}

function setButtonLoading(button, loading, textLoading = "Procesando...") {
  if (!button) return;
  if (loading) {
    button.dataset.originalText = button.textContent;
    button.textContent = textLoading;
    button.disabled = true;
  } else {
    button.textContent = button.dataset.originalText || button.textContent;
    button.disabled = false;
  }
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
  const value = String(rol).trim().toLowerCase();
  if (value === "usuario" || value === "user") return "cliente";
  if (value === "administrador" || value === "superusuario" || value === "superadmin" || value === "superuser" || value === "super_admin" || value === "super-admin") return "admin";
  return value;
}

function guardarSesion(data) {
  localStorage.setItem("access_token", data.access_token);
  if (data.refresh_token) localStorage.setItem("refresh_token", data.refresh_token);
  if (data.usuario) localStorage.setItem("usuario", JSON.stringify(data.usuario));
  actualizarNavbar();
}

function limpiarSesionLocal() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("usuario");
  localStorage.removeItem("id_negocio_actual");
  sessionStorage.removeItem("correo_2fa");
  sessionStorage.removeItem("mfa_mode");
}

function cerrarSesion() {
  limpiarSesionLocal();
  actualizarNavbar();
  setVisible(["inicio", "cta"]);
}

function cerrarSesionExpirada(mensaje = "Tu sesión expiró por inactividad. Inicia sesión nuevamente.") {
  limpiarSesionLocal();
  actualizarNavbar();
  setVisible(["login"]);
  mostrarMensaje("loginMsg", mensaje, true);
  showToast(mensaje, "info", 6500);
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
function formatearFechaCorta(fecha) {
  if (!fecha) return "sin fecha";

  const date = new Date(fecha);

  if (Number.isNaN(date.getTime())) {
    return String(fecha);
  }

  return date.toLocaleString("es-CO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}
function obtenerIdNegocio(n) {
  return Number(campoNegocio(n, "id_negocio", "id", "negocio_id"));
}

function guardarNegocioActual(negocio) {
  if (!negocio) return;
  const idNegocio = obtenerIdNegocio(negocio);
  if (idNegocio) localStorage.setItem("id_negocio_actual", String(idNegocio));
}

async function obtenerIdNegocioActual() {
  const guardado = Number(localStorage.getItem("id_negocio_actual"));
  if (guardado) return guardado;

  const negocio = await obtenerMiNegocio(true);
  const idNegocio = obtenerIdNegocio(negocio);
  if (idNegocio) {
    localStorage.setItem("id_negocio_actual", String(idNegocio));
    return idNegocio;
  }

  throw new Error("No se encontró el negocio asociado a tu cuenta. Registra primero tu negocio o vuelve al panel principal.");
}

const DIAS_SEMANA = {
  1: "Lunes",
  2: "Martes",
  3: "Miércoles",
  4: "Jueves",
  5: "Viernes",
  6: "Sábado",
  7: "Domingo",
  lunes: "Lunes",
  martes: "Martes",
  miercoles: "Miércoles",
  miércoles: "Miércoles",
  jueves: "Jueves",
  viernes: "Viernes",
  sabado: "Sábado",
  sábado: "Sábado",
  domingo: "Domingo",
};

function nombreDiaSemana(valor) {
  return DIAS_SEMANA[String(valor).toLowerCase()] || DIAS_SEMANA[Number(valor)] || `Día ${escapeHtml(valor)}`;
}

function diasSeleccionadosHorario() {
  return Array.from(document.querySelectorAll('input[name="horarioDias"]:checked')).map(input => Number(input.value));
}

function limpiarDiasHorario() {
  document.querySelectorAll('input[name="horarioDias"]').forEach(input => { input.checked = false; });
}

function renderNegocios(lista, contenedorId) {
  const contenedor = document.getElementById(contenedorId);
  if (!contenedor) return;

  if (!Array.isArray(lista) || lista.length === 0) {
    contenedor.innerHTML = `<div class="empty-state">No hay negocios registrados todavía.</div>`;
    return;
  }

  contenedor.innerHTML = lista.map(n => {
    const idNegocio = obtenerIdNegocio(n);
    const nombre = escapeHtml(campoNegocio(n, "nombre_negocio", "nombre", "name") || "Negocio sin nombre");
    const descripcion = escapeHtml(campoNegocio(n, "descripcion", "description") || "Sin descripción registrada");
    const direccion = escapeHtml(campoNegocio(n, "direccion", "address") || "Sin dirección");
    const telefono = escapeHtml(campoNegocio(n, "telefono", "phone") || "Sin teléfono");
    const correo = escapeHtml(campoNegocio(n, "email_negocio", "correo", "email") || "Sin correo");

    return `
      <article class="business-card clickable" onclick="abrirNegocioCliente(${idNegocio})">
        <div class="business-avatar">${nombre.charAt(0).toUpperCase()}</div>
        <div class="business-content">
          <h3>${nombre}</h3>
          <p>${descripcion}</p>
          <div class="business-meta">
            <span>📍 ${direccion}</span>
            <span>📞 ${telefono}</span>
            <span>✉️ ${correo}</span>
          </div>
          <button class="btn-primary tiny" type="button">Ver y agendar</button>
        </div>
      </article>
    `;
  }).join("");
}

// ─────────────────────────────────────────────
// FORMULARIOS
// ─────────────────────────────────────────────
function llenarSelectHorariosEmpleado(empleados) {
  const select = document.getElementById("horarioEmpleadoSelect");
  if (!select) return;
  const lista = Array.isArray(empleados) ? empleados : [];
  select.innerHTML = `<option value="">Selecciona empleado</option>` + lista.map(e => `
    <option value="${e.id_empleado}">${escapeHtml(`${e.nombre || ""} ${e.apellido || ""}`.trim() || "Empleado")} - ${escapeHtml(e.especialidad || "General")}</option>
  `).join("");
}

function seleccionarEmpleadoHorario(idEmpleado) {
  const select = document.getElementById("horarioEmpleadoSelect");
  if (select) select.value = String(idEmpleado);
  cargarHorariosEmpleadoSeleccionado();
}

async function cargarHorariosEmpleadoSeleccionado() {
  const idEmpleado = Number(document.getElementById("horarioEmpleadoSelect")?.value);
  const cont = document.getElementById("listaHorariosEmpleado");
  if (!cont) return;
  if (!idEmpleado) {
    cont.innerHTML = `<div class="empty-state">Selecciona un empleado para ver sus horarios.</div>`;
    return;
  }

  try {
    const data = await apiFetchConRutas(RUTAS_HORARIOS.map(r => `${r}${idEmpleado}`));
    const horarios = Array.isArray(data) ? data : (data.horarios || []);
    if (!horarios.length) {
      cont.innerHTML = `<div class="empty-state">Este empleado todavía no tiene horarios asignados.</div>`;
      return;
    }
    cont.innerHTML = horarios.map(h => `
      <article class="admin-item">
        <div><h4>${escapeHtml(h.dia_semana || "Día")}</h4><p>${escapeHtml(h.hora_inicio || "--:--")} - ${escapeHtml(h.hora_fin || "--:--")} · ${h.disponible === false ? "No disponible" : "Disponible"}</p></div>
        <div class="row-actions"><button onclick="eliminarHorario(${h.id_horario})">Eliminar</button></div>
      </article>
    `).join("");
  } catch (e) {
    cont.innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
  }
}

async function eliminarHorario(idHorario) {
  const ok = await pedirConfirmacion({
    title: "Eliminar horario",
    text: "Este horario dejará de estar disponible para el empleado.",
    confirmText: "Eliminar",
    danger: true
  });
  if (!ok) return;
  try {
    await apiFetchConRutas(RUTAS_HORARIOS.map(r => `${r}${idHorario}`), { method: "DELETE" });
    showToast("Horario eliminado correctamente.", "success");
    cargarHorariosEmpleadoSeleccionado();
  } catch (e) { showToast(friendlyError(e), "error"); }
}

async function cargarHorariosEmpleadoCliente(idEmpleado) {
  const info = document.getElementById("citaHorarioInfo");
  if (!info || !idEmpleado) return;
  info.textContent = "Consultando horarios del trabajador...";
  try {
    const data = await apiFetchConRutas(RUTAS_HORARIOS.map(r => `${r}${idEmpleado}`));
    const horarios = Array.isArray(data) ? data : (data.horarios || []);
    const disponibles = horarios.filter(h => h.disponible !== false);
    if (!disponibles.length) {
      info.textContent = "Este trabajador todavía no tiene horarios asignados. El negocio debe configurarlos desde Empleados → Horarios.";
      return;
    }
    info.innerHTML = "Horarios disponibles: " + disponibles.map(h => `${nombreDiaSemana(h.dia_semana)} ${escapeHtml(h.hora_inicio)}-${escapeHtml(h.hora_fin)}`).join(" · ");
  } catch (e) {
    info.textContent = "No se pudieron cargar los horarios. Revisa que exista /horarios-empleado/ en el backend desplegado.";
  }
}

async function iniciarConfiguracionMFA() {
  const btn = document.getElementById("btnMfaSetup");
  const box = document.getElementById("mfaSetupBox");
  const img = document.getElementById("mfaQrImage");
  const secret = document.getElementById("mfaSecret");
  if (!getToken()) return mostrarLogin();

  try {
    setButtonLoading(btn, true, "Generando QR...");
    const data = await apiFetch("/auth/mfa/setup", { method: "POST" });
    if (img) img.src = data.qr_base64 || "";
    if (secret) secret.textContent = data.secret ? `Clave manual: ${data.secret}` : "";
    if (box) box.style.display = "block";
    mostrarMensaje("perfilMsg", data.message || "Escanea el QR y confirma con el código de la app.", false);
    showToast("Escanea el QR con tu app autenticadora.", "success");
  } catch (error) {
    const msg = friendlyError(error);
    mostrarMensaje("perfilMsg", msg);
    showToast(msg, "error");
  } finally {
    setButtonLoading(btn, false);
  }
}

async function confirmarConfiguracionMFA() {
  const codigo = document.getElementById("mfaConfirmCodigo")?.value.trim();
  const form = document.getElementById("mfaConfirmForm");
  const btn = form?.querySelector("button[type='submit']");
  if (!/^\d{6}$/.test(codigo || "")) {
    const msg = "Ingresa un código de 6 dígitos generado por tu app autenticadora.";
    mostrarMensaje("perfilMsg", msg);
    showToast(msg, "error");
    return;
  }
  try {
    setButtonLoading(btn, true, "Confirmando...");
    const data = await apiFetch("/auth/mfa/confirm", {
      method: "POST",
      body: JSON.stringify({ codigo })
    });
    mostrarMensaje("perfilMsg", data.message || "MFA con aplicación autenticadora activado correctamente.", false);
    showToast("MFA con aplicación autenticadora activado correctamente.", "success");
    form?.reset();
  } catch (error) {
    const msg = friendlyError(error);
    mostrarMensaje("perfilMsg", msg);
    showToast(msg, "error");
  } finally {
    setButtonLoading(btn, false);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  actualizarNavbar();

  if (esPaginaDashboardRol()) {
    irDashboardPorRol();

    setTimeout(() => {
      finalizarCargaDashboard();
    }, 1200);
  }
  document.getElementById("registroForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const rolSeleccionado = document.querySelector('input[name="rolRegistro"]:checked')?.value || "cliente";
    const correo = document.getElementById("correo").value.trim().toLowerCase();
    const confirmarCorreo = document.getElementById("confirmarCorreo").value.trim().toLowerCase();

    const payload = {
      nombre: document.getElementById("nombre").value.trim(),
      apellido: document.getElementById("apellido").value.trim(),
      correo,
      telefono: document.getElementById("telefono").value.trim(),
      password: document.getElementById("password").value,
      rol: rolSeleccionado,
    };

    if (correo !== confirmarCorreo) {
      const msg = "Los correos no coinciden. Revisa el correo y la confirmación antes de continuar.";
      mostrarMensaje("registroMsg", msg);
      showToast(msg, "error");
      document.getElementById("confirmarCorreo")?.focus();
      return;
    }

    if (!validarPasswordFuerte(payload.password)) {
      const msg = mensajePoliticaPassword();
      mostrarMensaje("registroMsg", msg);
      showToast(msg, "error");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));

      if (res.status === 201 || res.ok) {
        mostrarMensaje("registroMsg", `Cuenta creada como ${ROLES[rolSeleccionado] || rolSeleccionado}. Revisa tu correo para activar la cuenta y luego inicia sesión.`, false);
        document.getElementById("registroForm").reset();
        setTimeout(mostrarLogin, 1200);
      } else {
        const msg = friendlyError(data);
        mostrarMensaje("registroMsg", msg);
        showToast(msg, "error");
      }
    } catch (error) {
      const msg = friendlyError(error) || "No se pudo conectar al servidor.";
      mostrarMensaje("registroMsg", msg);
      showToast(msg, "error");
    }
  });

  document.getElementById("forgotPasswordForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const correo = document.getElementById("forgotCorreo")?.value.trim().toLowerCase();
    const btn = document.getElementById("forgotPasswordBtn");

    if (!correo) {
      const msg = "Ingresa el correo asociado a tu cuenta.";
      mostrarMensaje("forgotPasswordMsg", msg);
      showToast(msg, "error");
      return;
    }

    try {
      setButtonLoading(btn, true, "Enviando...");
      await fetch(`${API_BASE}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ correo }),
      });

      const msg = "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.";
      mostrarMensaje("forgotPasswordMsg", msg, false);
      showToast(msg, "success", 6500);
      document.getElementById("forgotPasswordForm")?.reset();
    } catch (error) {
      const msg = "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.";
      mostrarMensaje("forgotPasswordMsg", msg, false);
      showToast(msg, "success", 6500);
    } finally {
      setButtonLoading(btn, false);
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

      if (res.ok && (data.requiere_mfa || data.requiere_mfa === true || data.metodo === "totp")) {
        sessionStorage.setItem("correo_2fa", data.correo || payload.correo);
        sessionStorage.setItem("mfa_mode", "totp");
        showToast("Verificación con app autenticadora requerida.", "info");
        window.location.href = "verificar-mfa.html";
        return;
      } else if (res.ok && data.requieres_2fa) {
        sessionStorage.setItem("correo_2fa", data.correo || payload.correo);
        sessionStorage.setItem("mfa_mode", "email");
        showToast("Te enviamos un código de seguridad al correo.", "success");
        window.location.href = "verificar-mfa.html";
        return;
      } else if (res.ok && data.requiere_configurar_mfa === true) {
        guardarSesion(data);
        sessionStorage.setItem("mfa_config_pendiente", "true");
        showToast("Debes configurar MFA con tu aplicación autenticadora.", "info");
        window.location.href = "mfa.html";
      } else if (res.ok && data.access_token) {
        guardarSesion(data);
        showToast("Inicio de sesión exitoso.", "success");
        irDashboardPorRol();
      } else {
        const msg = friendlyError(data.detail || data.message || "Credenciales inválidas.");
        mostrarMensaje("loginMsg", msg);
        showToast(msg, "error");
      }
    } catch (error) {
      const msg = friendlyError(error);
      mostrarMensaje("loginMsg", msg);
      showToast(msg, "error");
    }
  });

  document.getElementById("verify2faForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      correo: sessionStorage.getItem("correo_2fa"),
      codigo: document.getElementById("codigo2fa").value.trim(),
    };
    const mode = sessionStorage.getItem("mfa_mode") || loginVerificationMode || "email";
    const endpoint = mode === "totp" ? "/auth/mfa/verify" : "/auth/verify-2fa";
    const btn = document.getElementById("verify2faBtn");

    try {
      setButtonLoading(btn, true, "Verificando...");
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));

      if (res.ok && data.access_token) {
        guardarSesion(data);
        sessionStorage.removeItem("correo_2fa");
        sessionStorage.removeItem("mfa_mode");
        document.getElementById("verify2faForm")?.reset();
        showToast("Verificación completada correctamente.", "success");
        irDashboardPorRol();
      } else {
        const msg = friendlyError(data.detail || data.message || "Código inválido o expirado.");
        mostrarMensaje("verify2faMsg", msg);
        showToast(msg, "error");
      }
    } catch (error) {
      const msg = friendlyError(error);
      mostrarMensaje("verify2faMsg", msg);
      showToast(msg, "error");
    } finally {
      setButtonLoading(btn, false);
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
        const negocioCreado = data.negocio || data;
        guardarNegocioActual(negocioCreado);
        miNegocioCache = negocioCreado;
        const nombreNegocio = campoNegocio(negocioCreado, "nombre_negocio", "nombre") || payload.nombre;
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
      guardarNegocioActual(miNegocioCache);
      const span = document.getElementById("dashNombreNegocio");
      if (span) span.textContent = miNegocio ? campoNegocio(miNegocio, "nombre_negocio", "nombre") : "Sin negocio aún";
    })
    .catch(() => {});
}

function cargarDatosDashboardUsuario(usuario) {
  const nombre = `${usuario.nombre || ""} ${usuario.apellido || ""}`.trim() || usuario.correo;
  document.getElementById("userDashNombre").textContent = nombre;
}

function cargarDatosDashboardAdmin(usuario) {
  const nombre = `${usuario.nombre || ""} ${usuario.apellido || ""}`.trim() || usuario.correo || "Administrador";
  const el = document.getElementById("adminDashNombre");
  if (el) el.textContent = nombre;
}

async function validarSesionActiva({ silencioso = false } = {}) {
  const token = getToken();
  const usuario = getUsuario();
  if (!token || !usuario) return false;

  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { "Authorization": `Bearer ${token}` },
    });

    if (res.ok) {
      const data = await res.json().catch(() => null);
      if (data && typeof data === "object") {
        localStorage.setItem("usuario", JSON.stringify({ ...usuario, ...data }));
      }
      actualizarNavbar();
      return true;
    }

    if (res.status === 401 || res.status === 403) {
      cerrarSesionExpirada();
      return false;
    }

    if (!silencioso) {
      showToast("No pudimos validar tu sesión. Intenta nuevamente.", "error");
    }
    return false;
  } catch {
    if (!silencioso) {
      showToast("No se pudo validar la sesión con el servidor. Revisa tu conexión.", "error");
    }
    return true;
  }
}

async function checkSession() {
  const usuario = getUsuario();
  const token = getToken();
  const hash = window.location.hash;
  const pagina = paginaActual();

  if (!token || !usuario) {
    actualizarNavbar();

    if (pagina === "login.html" || hash === "#login") {
      mostrarLogin();
      return;
    }

    if (pagina === "registro.html") {
      mostrarRegistro();
      return;
    }

    if (pagina === "verificar-mfa.html") {
      mostrarVerifyMFA(sessionStorage.getItem("mfa_mode") || "totp");
      return;
    }

    if (pagina === "restablecer.html" || pagina === "activacion.html" || pagina === "mfa.html") {
      return;
    }

    if (esPaginaDashboardRol(pagina)) {
      window.location.href = "login.html";
      return;
    }

    setVisible(["inicio", "cta"]);
    return;
  }

  const sesionOk = await validarSesionActiva();
  if (!sesionOk) return;

  if (pagina === "login.html" || pagina === "registro.html" || pagina === "index.html" || esPaginaDashboardRol(pagina)) {
    irDashboardPorRol();
    return;
  }

  if (hash === "#login") {
    irDashboardPorRol();
  }
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
    } else if (res.status === 401 || res.status === 403) {
      cerrarSesionExpirada();
      return;
    } else {
      mostrarMensaje("perfilMsg", friendlyError(data.detail || data.message || "No se pudo cargar el perfil."));
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
    showToast("Solo las cuentas tipo negocio pueden registrar un negocio.", "error");
    return irDashboardPorRol();
  }
  mostrarRegistrarNegocio();
}

async function obtenerNegocios() {
  const token = getToken();
  const headers = token ? { "Authorization": `Bearer ${token}` } : {};
  const res = await fetch(`${API_BASE}/negocios/`, { headers });
  const data = await res.json().catch(() => []);
  if (!res.ok) {
    if (res.status === 401) {
      cerrarSesionExpirada();
      throw new Error("Tu sesión expiró por inactividad. Inicia sesión nuevamente.");
    }
    if (res.status === 403) throw new Error("No tienes permisos para consultar esta información.");
    throw new Error(friendlyError(data.detail || data.message || "No se pudieron cargar los negocios."));
  }
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
  horarios: "/horarios-empleado/",
  calificaciones: "/calificaciones/",
  pedidos: "/pedidos/",
  pagos: "/pagos/",
  pedidoDetalle: "/pedido-detalle/",
};


let negocioSeleccionado = null;
let empleadosNegocioSeleccionado = [];
let serviciosNegocioSeleccionado = [];
let horariosEmpleadoClienteCache = [];
let citasNegocioSeleccionadoCache = [];

function extraerMensajeError(data, status) {
  const texto = normalizarTextoError(data);
  return texto || `Error ${status}`;
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      if (res.status === 401) {
        cerrarSesionExpirada();
        throw new Error("Tu sesión expiró por inactividad. Inicia sesión nuevamente.");
      }
      if (res.status === 403) {
        throw new Error("No tienes permisos para realizar esta acción con tu usuario actual.");
      }
      throw new Error(friendlyError(extraerMensajeError(data, res.status)));
    }
    return data;
  } catch (error) {
    if (error instanceof TypeError || String(error.message).toLowerCase().includes("failed to fetch")) {
      throw new Error("No se pudo conectar con el backend. Verifica que el servicio de Render esté activo y que la ruta exista en Swagger.");
    }
    throw error;
  }
}

function esErrorRutaNoEncontrada(error) {
  const msg = String(error?.message || "").toLowerCase();
  return msg.includes("not found") || msg.includes("404") || msg.includes("ruta exista") || msg.includes("method not allowed");
}

async function apiFetchConRutas(paths, options = {}) {
  let ultimoError;
  for (const path of paths) {
    try {
      return await apiFetch(path, options);
    } catch (error) {
      ultimoError = error;
      if (!esErrorRutaNoEncontrada(error)) break;
    }
  }
  throw ultimoError;
}

const RUTAS_CITAS = ["/citas/"];
const RUTAS_HORARIOS = ["/horarios-empleado/", "/horarios-empleados/", "/horario-empleado/", "/horarios/", "/horario/"];
const RUTA_DISPONIBILIDAD_CITAS = "/citas/disponibilidad";

function asegurarRolNegocio() {
  const usuario = getUsuario();
  if (!usuario || !getToken()) { mostrarLogin(); return false; }
  if (normalizarRol(usuario.rol) !== "negocio" && normalizarRol(usuario.rol) !== "admin") {
    showToast("Esta opción es solo para cuentas tipo negocio.", "error");
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
  guardarNegocioActual(miNegocioCache);
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
      acciones = `<button onclick="seleccionarEmpleadoHorario(${id})">Horarios</button><button onclick="editarEmpleado(${id})">Editar</button><button onclick="eliminarEmpleado(${id})">Eliminar</button>`;
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

function esRolClienteActual() {
  const usuario = getUsuario();
  return normalizarRol(usuario?.rol) === "cliente";
}

function configurarFormularioAgendamientoPorRol() {
  const form = document.getElementById("agendarCitaForm");
  const msg = document.getElementById("agendarCitaMsg");
  if (!form) return;

  if (!esRolClienteActual()) {
    form.classList.add("blocked-form");
    form.querySelectorAll("select,input,textarea,button").forEach(el => el.disabled = true);
    if (msg) {
      msg.textContent = "Estás viendo esta barbería con una cuenta de negocio. Para agendar una cita debes iniciar sesión con una cuenta tipo Usuario/Cliente.";
      msg.style.color = "#e8c97a";
      msg.style.display = "block";
    }
    return;
  }

  form.classList.remove("blocked-form");
  form.querySelectorAll("select,input,textarea,button").forEach(el => el.disabled = false);
  if (msg) {
    msg.textContent = "";
    msg.style.display = "none";
  }
}

async function irGestionEmpleados() { mostrarGestion("gestion-empleados"); await cargarEmpleados(); }

async function abrirNegocioCliente(idNegocio) {
  const token = getToken();
  const usuario = getUsuario();

  if (!token || !usuario) {
    mostrarLogin();
    mostrarMensaje("loginMsg", "Inicia sesión como usuario para agendar una cita.");
    return;
  }

  try {
    const negocio = negociosCache.find(n => obtenerIdNegocio(n) === Number(idNegocio)) || await apiFetch(`/negocios/${idNegocio}`);
    negocioSeleccionado = negocio;

    const nombre = campoNegocio(negocio, "nombre_negocio", "nombre") || "Negocio";
    document.getElementById("detalleNegocioNombre").textContent = nombre;
    document.getElementById("detalleNegocioDescripcion").textContent = campoNegocio(negocio, "descripcion") || "Sin descripción registrada.";
    document.getElementById("detalleNegocioDireccion").textContent = campoNegocio(negocio, "direccion") || "Sin dirección";
    document.getElementById("detalleNegocioTelefono").textContent = campoNegocio(negocio, "telefono") || "Sin teléfono";
    document.getElementById("detalleNegocioCorreo").textContent = campoNegocio(negocio, "email_negocio", "correo", "email") || "Sin correo";

    await cargarDatosAgendamiento(idNegocio);
    mostrarDetalleNegocio();
    configurarFormularioAgendamientoPorRol();
  } catch (e) {
    mostrarMensaje("usuarioNegociosMsg", e.message || "No se pudo abrir el negocio.");
  }
}

async function cargarDatosAgendamiento(idNegocio) {
  const [empleados, servicios] = await Promise.all([
    apiFetch(API_PATHS.empleados),
    apiFetch(API_PATHS.servicios),
  ]);

  empleadosNegocioSeleccionado = (Array.isArray(empleados) ? empleados : [])
    .filter(e => Number(e.id_negocio) === Number(idNegocio) && (e.estado || "activo") === "activo");

  serviciosNegocioSeleccionado = (Array.isArray(servicios) ? servicios : [])
    .filter(s => Number(s.id_negocio) === Number(idNegocio) && (s.estado || "activo") === "activo");

  renderEmpleadosCliente();
  renderServiciosCliente();
  llenarSelectAgendamiento();
  horariosEmpleadoClienteCache = [];
  limpiarHorasDisponibles();
  await cargarCitasNegocioParaDisponibilidad();
}

function renderEmpleadosCliente() {
  const contenedor = document.getElementById("detalleEmpleadosNegocio");
  if (!contenedor) return;

  if (!empleadosNegocioSeleccionado.length) {
    contenedor.innerHTML = `<div class="empty-state">Este negocio todavía no tiene empleados activos.</div>`;
    return;
  }

  contenedor.innerHTML = empleadosNegocioSeleccionado.map(e => `
    <div class="mini-card">
      <strong>${escapeHtml(`${e.nombre || ""} ${e.apellido || ""}`.trim() || "Empleado")}</strong>
      <span>${escapeHtml(e.especialidad || "Sin especialidad")}</span>
      <small>${escapeHtml(e.telefono || "Sin teléfono")}</small>
    </div>
  `).join("");
}

function renderServiciosCliente() {
  const contenedor = document.getElementById("detalleServiciosNegocio");
  if (!contenedor) return;

  if (!serviciosNegocioSeleccionado.length) {
    contenedor.innerHTML = `<div class="empty-state">Este negocio todavía no tiene servicios activos.</div>`;
    return;
  }

  contenedor.innerHTML = serviciosNegocioSeleccionado.map(s => `
    <div class="mini-card">
      <strong>${escapeHtml(s.nombre || "Servicio")}</strong>
      <span>${escapeHtml(s.descripcion || "Sin descripción")}</span>
      <small>${Number(s.duracion_minutos || 40)} min · $${Number(s.precio || 0).toLocaleString("es-CO")}</small>
    </div>
  `).join("");
}

function llenarSelectAgendamiento() {
  const selectEmpleado = document.getElementById("citaEmpleado");
  const selectServicio = document.getElementById("citaServicio");
  if (!selectEmpleado || !selectServicio) return;

  selectEmpleado.innerHTML = `<option value="">Selecciona un trabajador</option>` + empleadosNegocioSeleccionado.map(e => `
    <option value="${e.id_empleado}">${escapeHtml(`${e.nombre || ""} ${e.apellido || ""}`.trim() || "Empleado")} - ${escapeHtml(e.especialidad || "General")}</option>
  `).join("");

  selectServicio.innerHTML = `<option value="">Selecciona un servicio</option>` + serviciosNegocioSeleccionado.map(s => `
    <option value="${s.id_servicio}" data-duracion="${Number(s.duracion_minutos || 40)}" data-precio="${Number(s.precio || 0)}">${escapeHtml(s.nombre || "Servicio")} - ${Number(s.duracion_minutos || 40)} min - $${Number(s.precio || 0).toLocaleString("es-CO")}</option>
  `).join("");
}

function normalizarHoraApi(hora) {
  if (!hora) return "";
  const partes = String(hora).split(":");
  const hh = String(partes[0] || "00").padStart(2, "0");
  const mm = String(partes[1] || "00").padStart(2, "0");
  const ss = String(partes[2] || "00").padStart(2, "0");
  return `${hh}:${mm}:${ss}`;
}

function sumarMinutosHora(hora, minutos) {
  const [hh, mm] = String(hora || "").split(":").map(Number);
  if (Number.isNaN(hh) || Number.isNaN(mm)) return "";
  const total = hh * 60 + mm + Number(minutos || 40);
  const h2 = String(Math.floor(total / 60) % 24).padStart(2, "0");
  const m2 = String(total % 60).padStart(2, "0");
  return `${h2}:${m2}:00`;
}

function minutosDesdeHora(hora) {
  const partes = String(hora || "").split(":").map(Number);
  const hh = Number(partes[0]);
  const mm = Number(partes[1] || 0);
  if (Number.isNaN(hh) || Number.isNaN(mm)) return null;
  return hh * 60 + mm;
}

function horaDesdeMinutos(totalMinutos) {
  const total = Math.max(0, Number(totalMinutos || 0));
  const hh = String(Math.floor(total / 60) % 24).padStart(2, "0");
  const mm = String(total % 60).padStart(2, "0");
  return `${hh}:${mm}:00`;
}

function formatearHoraVisible(hora) {
  const mins = minutosDesdeHora(hora);
  if (mins === null) return String(hora || "");
  const h24 = Math.floor(mins / 60) % 24;
  const mm = String(mins % 60).padStart(2, "0");
  const periodo = h24 >= 12 ? "p. m." : "a. m.";
  let h12 = h24 % 12;
  if (h12 === 0) h12 = 12;
  return `${h12}:${mm} ${periodo}`;
}

function numeroDiaSemanaFecha(fecha) {
  if (!fecha) return null;
  const d = new Date(`${fecha}T00:00:00`);
  if (Number.isNaN(d.getTime())) return null;
  const jsDay = d.getDay();
  return jsDay === 0 ? 7 : jsDay;
}

function normalizarDiaHorario(valor) {
  if (valor === null || valor === undefined) return null;
  const texto = String(valor).trim().toLowerCase();
  const mapa = {
    "1": 1, lunes: 1,
    "2": 2, martes: 2,
    "3": 3, miercoles: 3, miércoles: 3,
    "4": 4, jueves: 4,
    "5": 5, viernes: 5,
    "6": 6, sabado: 6, sábado: 6,
    "7": 7, domingo: 7,
    "0": 7
  };
  return mapa[texto] || null;
}

function obtenerDuracionServicioSeleccionado() {
  const idServicio = Number(document.getElementById("citaServicio")?.value);
  const servicio = serviciosNegocioSeleccionado.find(s => Number(s.id_servicio) === idServicio);
  return Number(servicio?.duracion_minutos || 40);
}

function limpiarHorasDisponibles(mensaje = "Selecciona trabajador, servicio y fecha") {
  const selectHora = document.getElementById("citaHora");
  if (!selectHora) return;
  selectHora.innerHTML = `<option value="">${escapeHtml(mensaje)}</option>`;
  selectHora.disabled = true;
}

function citaSeCruza(inicioA, finA, inicioB, finB) {
  const a1 = minutosDesdeHora(inicioA);
  const a2 = minutosDesdeHora(finA);
  const b1 = minutosDesdeHora(inicioB);
  const b2 = minutosDesdeHora(finB);
  if ([a1, a2, b1, b2].some(v => v === null)) return false;
  return a1 < b2 && b1 < a2;
}

function generarHorariosLocales({ fecha, idEmpleado, duracion }) {
  const dia = numeroDiaSemanaFecha(fecha);
  if (!dia || !Array.isArray(horariosEmpleadoClienteCache)) return [];

  const horariosDelDia = horariosEmpleadoClienteCache.filter(h => {
    const diaHorario = normalizarDiaHorario(h.dia_semana);
    return h.disponible !== false && diaHorario === dia;
  });

  const citasOcupadas = (Array.isArray(citasNegocioSeleccionadoCache) ? citasNegocioSeleccionadoCache : [])
    .filter(c => Number(c.id_empleado) === Number(idEmpleado))
    .filter(c => String(c.fecha || "").slice(0, 10) === String(fecha))
    .filter(c => !["cancelada", "cancelado", "rechazada", "rechazado", "anulada", "anulado"].includes(String(c.estado || "").toLowerCase()));

  const slots = [];
  horariosDelDia.forEach(h => {
    const inicio = minutosDesdeHora(h.hora_inicio);
    const fin = minutosDesdeHora(h.hora_fin);
    if (inicio === null || fin === null || fin <= inicio) return;

    for (let actual = inicio; actual + duracion <= fin; actual += duracion) {
      const horaInicio = horaDesdeMinutos(actual);
      const horaFin = horaDesdeMinutos(actual + duracion);
      const ocupado = citasOcupadas.some(c => citaSeCruza(horaInicio, horaFin, c.hora_inicio, c.hora_fin));
      if (!ocupado) slots.push({ hora_inicio: horaInicio, hora_fin: horaFin });
    }
  });

  const vistos = new Set();
  return slots
    .sort((a, b) => minutosDesdeHora(a.hora_inicio) - minutosDesdeHora(b.hora_inicio))
    .filter(s => {
      if (vistos.has(s.hora_inicio)) return false;
      vistos.add(s.hora_inicio);
      return true;
    });
}

async function consultarDisponibilidadBackend({ idEmpleado, idServicio, fecha }) {
  const query = `?id_empleado=${encodeURIComponent(idEmpleado)}&id_servicio=${encodeURIComponent(idServicio)}&fecha=${encodeURIComponent(fecha)}`;
  const data = await apiFetch(`${RUTA_DISPONIBILIDAD_CITAS}${query}`);
  const disponibles = data?.horarios_disponibles || [];

  if (!Array.isArray(disponibles)) return [];

  return disponibles.map(item => ({
    hora_inicio: normalizarHoraApi(item.hora_inicio),
    hora_fin: normalizarHoraApi(item.hora_fin),
  })).filter(s => s.hora_inicio && s.hora_fin);
}

async function cargarCitasNegocioParaDisponibilidad() {
  if (!negocioSeleccionado) {
    citasNegocioSeleccionadoCache = [];
    return;
  }
  const idNegocio = obtenerIdNegocio(negocioSeleccionado);
  try {
    const data = await apiFetchConRutas([`/citas/negocio/${idNegocio}`, `/cita/negocio/${idNegocio}`]);
    citasNegocioSeleccionadoCache = Array.isArray(data) ? data : (data.citas || []);
  } catch (_) {
    // Si el usuario cliente no tiene permiso para consultar todas las citas del negocio,
    // el frontend igualmente mostrará horarios base; el backend debe validar cruces al crear.
    citasNegocioSeleccionadoCache = [];
  }
}

async function actualizarOpcionesHoraDisponible() {
  const idEmpleado = Number(document.getElementById("citaEmpleado")?.value);
  const idServicio = Number(document.getElementById("citaServicio")?.value);
  const fecha = document.getElementById("citaFecha")?.value;
  const info = document.getElementById("citaHorarioInfo");
  const selectHora = document.getElementById("citaHora");
  if (!selectHora) return;

  if (!idEmpleado || !idServicio || !fecha) {
    limpiarHorasDisponibles("Selecciona trabajador, servicio y fecha");
    if (info) info.textContent = "Selecciona trabajador, servicio y fecha para consultar la disponibilidad real.";
    return;
  }

  const duracion = obtenerDuracionServicioSeleccionado();
  limpiarHorasDisponibles("Consultando disponibilidad...");
  if (info) info.textContent = `Consultando horarios disponibles para un servicio de ${duracion} minutos...`;

  try {
    const slots = await consultarDisponibilidadBackend({ idEmpleado, idServicio, fecha });

    if (!slots.length) {
      limpiarHorasDisponibles("No hay horarios disponibles");
      if (info) info.textContent = "No hay horarios disponibles para ese trabajador, servicio y fecha.";
      return;
    }

    selectHora.disabled = false;
    selectHora.innerHTML = `<option value="">Selecciona una hora disponible</option>` + slots.map(s => `
      <option value="${escapeHtml(s.hora_inicio)}" data-fin="${escapeHtml(s.hora_fin)}">
        ${escapeHtml(formatearHoraVisible(s.hora_inicio))} - ${escapeHtml(formatearHoraVisible(s.hora_fin))}
      </option>
    `).join("");
    if (info) info.textContent = "Horarios disponibles consultados desde la agenda real del trabajador.";
  } catch (error) {
    limpiarHorasDisponibles("No se pudieron cargar horarios");
    const msg = friendlyError(error);
    if (info) info.textContent = msg;
    showToast(msg, "error");
  }
}

async function agendarCitaCliente(e) {
  e.preventDefault();

  const usuario = getUsuario();
  if (!usuario || !getToken()) return mostrarLogin();

  if (normalizarRol(usuario.rol) !== "cliente") {
    return mostrarMensaje("agendarCitaMsg", "Para agendar debes ingresar con una cuenta tipo Usuario/Cliente. Las cuentas de negocio solo gestionan empleados, servicios, inventario y citas recibidas.");
  }

  if (!negocioSeleccionado) return mostrarMensaje("agendarCitaMsg", "Primero selecciona una barbería.");

  const idNegocio = obtenerIdNegocio(negocioSeleccionado);
  const idEmpleado = Number(document.getElementById("citaEmpleado").value);
  const idServicio = Number(document.getElementById("citaServicio").value);
  const fecha = document.getElementById("citaFecha").value;
  const selectHora = document.getElementById("citaHora");
  const horaInicio = normalizarHoraApi(selectHora?.value);
  const horaFinSeleccionada = normalizarHoraApi(selectHora?.selectedOptions?.[0]?.dataset?.fin);
  const observaciones = document.getElementById("citaObservaciones").value.trim() || null;

  if (!idEmpleado || !idServicio || !fecha || !horaInicio) {
    mostrarMensaje("agendarCitaMsg", "Completa trabajador, servicio, fecha y selecciona una hora disponible.");
    return;
  }

  try {
    const citaPayload = {
      id_negocio: idNegocio,
      id_empleado: idEmpleado,
      id_servicio: idServicio,
      fecha,
      hora_inicio: horaInicio,
      observaciones,
    };

    console.log("Payload cita enviado:", citaPayload);

    await apiFetchConRutas(RUTAS_CITAS, {
      method: "POST",
      body: JSON.stringify(citaPayload),
    });

    e.target.reset();
    limpiarHorasDisponibles();
    const rango = horaFinSeleccionada ? ` de ${formatearHoraVisible(horaInicio)} a ${formatearHoraVisible(horaFinSeleccionada)}` : ` a las ${formatearHoraVisible(horaInicio)}`;
    mostrarMensaje("agendarCitaMsg", `Cita agendada correctamente${rango}.`, false);
    showToast("Cita agendada correctamente.", "success");
  } catch (error) {
    mostrarMensaje("agendarCitaMsg", error.message || "No se pudo agendar la cita.");
  }
}

async function irGestionServicios() { mostrarGestion("gestion-servicios"); await cargarServicios(); }
async function irGestionProductos() { mostrarGestion("gestion-productos"); await cargarProductos(); }
async function irGestionCitas() { mostrarGestion("gestion-citas"); await cargarCitas(); }

async function cargarEmpleados() {
  try {
    const empleados = await apiFetch(API_PATHS.empleados);
    empleadosCache = Array.isArray(empleados) ? empleados : [];
    renderAdminList(empleadosCache, "listaEmpleados", "empleado");
    llenarSelectHorariosEmpleado(empleadosCache);
    mostrarMensaje("empleadoMsg", "", false);
  } catch (e) {
    document.getElementById("listaEmpleados").innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
  }
}
async function cargarServicios() {
  try { renderAdminList(await apiFetch(API_PATHS.servicios), "listaServicios", "servicio"); mostrarMensaje("servicioMsg", "", false); }
  catch (e) { document.getElementById("listaServicios").innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`; }
}
async function cargarProductos() {
  try {
    const productos = await apiFetch(API_PATHS.productos);
    let lista = Array.isArray(productos) ? productos : [];
    const idNegocio = Number(localStorage.getItem("id_negocio_actual")) || Number(obtenerIdNegocio(miNegocioCache || {}));
    if (idNegocio) lista = lista.filter(p => !p.id_negocio || Number(p.id_negocio) === idNegocio);
    renderAdminList(lista, "listaProductos", "producto");
    mostrarMensaje("productoMsg", "", false);
  }
  catch (e) { document.getElementById("listaProductos").innerHTML = `<div class="empty-state">${escapeHtml(friendlyError(e))}</div>`; }
}
async function cargarCitas() {
  try {
    const negocio = await obtenerMiNegocio(true);
    if (!negocio?.id_negocio) throw new Error("Primero debes tener un negocio registrado.");
    renderAdminList(await apiFetchConRutas([`/citas/negocio/${negocio.id_negocio}`, `/cita/negocio/${negocio.id_negocio}`]), "listaCitas", "cita");
    mostrarMensaje("citasMsg", "", false);
  } catch (e) {
    document.getElementById("listaCitas").innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
  }
}

function llenarSelectHorariosEmpleado(empleados) {
  const select = document.getElementById("horarioEmpleadoSelect");
  if (!select) return;
  const lista = Array.isArray(empleados) ? empleados : [];
  select.innerHTML = `<option value="">Selecciona empleado</option>` + lista.map(e => `
    <option value="${e.id_empleado}">${escapeHtml(`${e.nombre || ""} ${e.apellido || ""}`.trim() || "Empleado")} - ${escapeHtml(e.especialidad || "General")}</option>
  `).join("");
}

function seleccionarEmpleadoHorario(idEmpleado) {
  const select = document.getElementById("horarioEmpleadoSelect");
  if (select) select.value = String(idEmpleado);
  cargarHorariosEmpleadoSeleccionado();
}

async function cargarHorariosEmpleadoSeleccionado() {
  const idEmpleado = Number(document.getElementById("horarioEmpleadoSelect")?.value);
  const cont = document.getElementById("listaHorariosEmpleado");
  if (!cont) return;
  if (!idEmpleado) {
    cont.innerHTML = `<div class="empty-state">Selecciona un empleado para ver sus horarios.</div>`;
    return;
  }

  try {
    const data = await apiFetchConRutas(RUTAS_HORARIOS.map(r => `${r}${idEmpleado}`));
    const horarios = Array.isArray(data) ? data : (data.horarios || []);
    if (!horarios.length) {
      cont.innerHTML = `<div class="empty-state">Este empleado todavía no tiene horarios asignados.</div>`;
      return;
    }
    cont.innerHTML = horarios.map(h => `
      <article class="admin-item">
        <div><h4>${escapeHtml(h.dia_semana || "Día")}</h4><p>${escapeHtml(h.hora_inicio || "--:--")} - ${escapeHtml(h.hora_fin || "--:--")} · ${h.disponible === false ? "No disponible" : "Disponible"}</p></div>
        <div class="row-actions"><button onclick="eliminarHorario(${h.id_horario})">Eliminar</button></div>
      </article>
    `).join("");
  } catch (e) {
    cont.innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
  }
}

async function eliminarHorario(idHorario) {
  const ok = await pedirConfirmacion({
    title: "Eliminar horario",
    text: "Este horario dejará de estar disponible para el empleado.",
    confirmText: "Eliminar",
    danger: true
  });
  if (!ok) return;
  try {
    await apiFetchConRutas(RUTAS_HORARIOS.map(r => `${r}${idHorario}`), { method: "DELETE" });
    showToast("Horario eliminado correctamente.", "success");
    cargarHorariosEmpleadoSeleccionado();
  } catch (e) { showToast(friendlyError(e), "error"); }
}

async function cargarHorariosEmpleadoCliente(idEmpleado) {
  const info = document.getElementById("citaHorarioInfo");
  horariosEmpleadoClienteCache = [];
  limpiarHorasDisponibles();
  if (!info || !idEmpleado) {
    await actualizarOpcionesHoraDisponible();
    return;
  }

  info.textContent = "Consultando horarios del trabajador...";
  try {
    const data = await apiFetchConRutas(RUTAS_HORARIOS.map(r => `${r}${idEmpleado}`));
    const horarios = Array.isArray(data) ? data : (data.horarios || []);
    horariosEmpleadoClienteCache = horarios.filter(h => h.disponible !== false);
    if (!horariosEmpleadoClienteCache.length) {
      info.textContent = "Este trabajador todavía no tiene horarios asignados. El negocio debe configurarlos desde Empleados → Horarios.";
      await actualizarOpcionesHoraDisponible();
      return;
    }
    info.innerHTML = "Horarios del trabajador: " + horariosEmpleadoClienteCache.map(h => `${nombreDiaSemana(h.dia_semana)} ${escapeHtml(h.hora_inicio)}-${escapeHtml(h.hora_fin)}`).join(" · ");
    await actualizarOpcionesHoraDisponible();
  } catch (e) {
    info.textContent = "No se pudieron cargar los horarios del trabajador. El backend debe exponer horarios por empleado para calcular disponibilidad.";
    await actualizarOpcionesHoraDisponible();
  }
}

// ─────────────────────────────────────────────
// MÓDULOS USUARIO: MIS CITAS / CALIFICACIONES / PEDIDOS / PAGOS
// ─────────────────────────────────────────────
let misCitasCache = [];
let misCalificacionesCache = [];
let productosUsuarioCache = [];
let misPedidosCache = [];
let misPagosCache = [];

function obtenerIdUsuarioActual() {
  const usuario = getUsuario();
  return Number(usuario?.id_usuario || usuario?.id || usuario?.usuario_id);
}

function asegurarRolCliente() {
  const usuario = getUsuario();
  if (!usuario || !getToken()) { mostrarLogin(); return false; }
  if (normalizarRol(usuario.rol) !== "cliente" && normalizarRol(usuario.rol) !== "admin") {
    showToast("Esta opción es para cuentas tipo usuario/cliente.", "error");
    irDashboardPorRol();
    return false;
  }
  return true;
}

function mostrarModuloCliente(id) {
  if (!asegurarRolCliente()) return;
  setVisible([id]);
}

function fechaHoraCita(cita, fin = false) {
  const fecha = cita.fecha || String(cita.fecha_hora_inicio || "").slice(0, 10);
  const hora = fin
    ? (cita.hora_fin || String(cita.fecha_hora_fin || "").slice(11, 19))
    : (cita.hora_inicio || String(cita.fecha_hora_inicio || "").slice(11, 19));
  if (!fecha || !hora) return null;
  return new Date(`${fecha}T${String(hora).slice(0, 8)}`);
}

function citaYaPaso(cita) {
  const fin = fechaHoraCita(cita, true) || fechaHoraCita(cita, false);
  return fin ? fin.getTime() < Date.now() : false;
}

function estadoVisualCita(cita) {
  const estado = String(cita.estado || "pendiente").toLowerCase();
  if (estado === "cancelada" || estado === "cancelado") return "Cancelada";
  if (citaYaPaso(cita)) return "Ya pasó";
  return estado.charAt(0).toUpperCase() + estado.slice(1);
}

function negocioNombrePorId(idNegocio) {
  const n = negociosCache.find(x => Number(obtenerIdNegocio(x)) === Number(idNegocio));
  return campoNegocio(n, "nombre_negocio", "nombre") || `Negocio #${idNegocio}`;
}

function empleadoNombrePorId(idEmpleado) {
  const e = empleadosCache.find(x => Number(x.id_empleado) === Number(idEmpleado));
  return e ? `${e.nombre || ""} ${e.apellido || ""}`.trim() : `Empleado #${idEmpleado}`;
}

async function irMisCitas() {
  mostrarModuloCliente("mis-citas-usuario");
  await cargarMisCitas();
}

async function cargarMisCitas() {
  const cont = document.getElementById("listaMisCitas");
  try {
    const idUsuario = obtenerIdUsuarioActual();
    if (!idUsuario) throw new Error("No se pudo identificar el usuario actual.");
    if (!negociosCache.length) negociosCache = await obtenerNegocios();
    try { empleadosCache = await apiFetch(API_PATHS.empleados); } catch { empleadosCache = []; }
    const data = await apiFetch(`/citas/cliente/${idUsuario}`);
    misCitasCache = Array.isArray(data) ? data : [];
    renderMisCitas();
    mostrarMensaje("misCitasMsg", "", false);
  } catch (e) {
    if (cont) cont.innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
  }
}

function renderMisCitas() {
  const cont = document.getElementById("listaMisCitas");
  if (!cont) return;
  if (!misCitasCache.length) {
    cont.innerHTML = `<div class="empty-state">Todavía no tienes citas registradas.</div>`;
    return;
  }
  cont.innerHTML = misCitasCache.map(cita => {
    const id = cita.id_cita;
    const fecha = cita.fecha || String(cita.fecha_hora_inicio || "").slice(0,10);
    const inicio = cita.hora_inicio || String(cita.fecha_hora_inicio || "").slice(11,16);
    const fin = cita.hora_fin || String(cita.fecha_hora_fin || "").slice(11,16);
    const estado = estadoVisualCita(cita);
    const cancelada = String(cita.estado || "").toLowerCase().includes("cancel");
    const puedeCalificar = citaYaPaso(cita) && !cancelada;
    const puedeCancelar = !citaYaPaso(cita) && !cancelada;
    return `<article class="admin-item">
      <div>
        <h4>${escapeHtml(negocioNombrePorId(cita.id_negocio))}</h4>
        <p>${escapeHtml(fecha)} · ${escapeHtml(inicio)} - ${escapeHtml(fin)} · ${escapeHtml(empleadoNombrePorId(cita.id_empleado))}</p>
        <span class="status-pill ${citaYaPaso(cita) ? 'done' : 'pending'}">${escapeHtml(estado)}</span>
      </div>
      <div class="row-actions">
        ${puedeCalificar ? `<button onclick="calificarCita(${id}, ${cita.id_negocio})">Calificar</button>` : ""}
        ${puedeCancelar ? `<button onclick="cancelarMiCita(${id})">Cancelar</button>` : ""}
        ${!cancelada ? `<button onclick="pagarCitaInfo(${id})">Pagar cita</button>` : ""}
      </div>
    </article>`;
  }).join("");
}

async function cancelarMiCita(idCita) {
  const ok = await pedirConfirmacion({
    title: "Cancelar cita",
    text: "La cita será cancelada y ya no aparecerá como activa.",
    confirmText: "Cancelar cita",
    danger: true
  });
  if (!ok) return;
  try {
    await apiFetch(`${API_PATHS.citas}${idCita}`, { method: "DELETE" });
    showToast("Cita cancelada correctamente.", "success");
    await cargarMisCitas();
  } catch (e) { showToast(friendlyError(e), "error"); }
}

async function calificarCita(idCita, idNegocio) {
  const result = await openUiModal({
    eyebrow: "Opinión",
    title: "Calificar cita",
    text: "Cuéntanos cómo fue tu experiencia. Tu opinión ayuda al negocio a mejorar.",
    confirmText: "Guardar calificación",
    fields: [
      { id: "puntuacion", label: "Puntuación de 1 a 5", type: "number", min: 1, max: 5, step: 1, value: 5 },
      { id: "comentario", label: "Comentario", type: "textarea", value: "Buen servicio", required: false }
    ]
  });
  if (!result) return;
  const puntuacion = Number(result.puntuacion);
  if (!Number.isInteger(puntuacion) || puntuacion < 1 || puntuacion > 5) {
    showToast("La puntuación debe estar entre 1 y 5.", "error");
    return;
  }
  try {
    await apiFetch(API_PATHS.calificaciones, {
      method: "POST",
      body: JSON.stringify({ id_negocio: Number(idNegocio), id_cita: Number(idCita), puntuacion, comentario: result.comentario || "" })
    });
    showToast("Calificación registrada correctamente.", "success");
    await cargarMisCalificaciones();
  } catch (e) { showToast(friendlyError(e), "error"); }
}

function pagarCitaInfo(idCita) {
  openUiModal({
    eyebrow: "Pagos",
    title: "Pago de cita no disponible aún",
    text: `La cita #${idCita} ya se puede listar y calificar. Para pagar citas directamente falta que el backend acepte pagos asociados a id_cita o que exista una ruta específica de pagos de citas.`,
    confirmText: "Entendido",
    showCancel: false
  });
}

async function irMisCalificaciones() {
  mostrarModuloCliente("mis-calificaciones-usuario");
  await cargarMisCalificaciones();
}

async function cargarMisCalificaciones() {
  const cont = document.getElementById("listaMisCalificaciones");
  try {
    const data = await apiFetch(API_PATHS.calificaciones);
    misCalificacionesCache = Array.isArray(data) ? data : [];
    if (!misCalificacionesCache.length) {
      cont.innerHTML = `<div class="empty-state">Todavía no tienes calificaciones registradas.</div>`;
      return;
    }
    cont.innerHTML = misCalificacionesCache.map(c => `<article class="admin-item">
      <div><h4>${"★".repeat(Number(c.puntuacion || 0))}${"☆".repeat(Math.max(0, 5 - Number(c.puntuacion || 0)))}</h4><p>Cita #${escapeHtml(c.id_cita || "—")} · ${escapeHtml(c.comentario || "Sin comentario")}</p></div>
      <div class="row-actions"><button onclick="eliminarCalificacion(${c.id_calificacion})">Eliminar</button></div>
    </article>`).join("");
    mostrarMensaje("misCalificacionesMsg", "", false);
  } catch (e) {
    if (cont) cont.innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
  }
}

async function eliminarCalificacion(id) {
  const ok = await pedirConfirmacion({
    title: "Eliminar calificación",
    text: "Esta opinión se eliminará de tu historial.",
    confirmText: "Eliminar",
    danger: true
  });
  if (!ok) return;
  try { await apiFetch(`${API_PATHS.calificaciones}${id}`, { method: "DELETE" }); showToast("Calificación eliminada.", "success"); cargarMisCalificaciones(); }
  catch (e) { showToast(friendlyError(e), "error"); }
}

async function irTiendaUsuario() {
  mostrarModuloCliente("tienda-usuario");
  await cargarProductosUsuario();
}

async function cargarProductosUsuario() {
  const cont = document.getElementById("listaProductosUsuario");
  try {
    if (!negociosCache.length) negociosCache = await obtenerNegocios();
    const data = await apiFetch(API_PATHS.productos);
    productosUsuarioCache = Array.isArray(data) ? data.filter(p => String(p.estado || "activo").toLowerCase() === "activo") : [];
    renderProductosUsuario(productosUsuarioCache);
    mostrarMensaje("tiendaUsuarioMsg", "", false);
  } catch (e) {
    if (cont) cont.innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
  }
}

function filtrarProductosUsuario() {
  const q = document.getElementById("buscarProductoUsuario")?.value.toLowerCase().trim() || "";
  if (!q) return renderProductosUsuario(productosUsuarioCache);
  renderProductosUsuario(productosUsuarioCache.filter(p => [p.nombre, p.descripcion, negocioNombrePorId(p.id_negocio)].join(" ").toLowerCase().includes(q)));
}

function renderProductosUsuario(productos) {
  const cont = document.getElementById("listaProductosUsuario");
  if (!cont) return;
  if (!productos.length) {
    cont.innerHTML = `<div class="empty-state">No hay productos activos disponibles.</div>`;
    return;
  }
  cont.innerHTML = productos.map(p => `<article class="business-card">
    <div class="business-avatar">${escapeHtml(String(p.nombre || "P").charAt(0).toUpperCase())}</div>
    <div class="business-content">
      <h3>${escapeHtml(p.nombre || "Producto")}</h3>
      <p>${escapeHtml(p.descripcion || "Sin descripción")}</p>
      <div class="business-meta"><span>${escapeHtml(negocioNombrePorId(p.id_negocio))}</span><span>Stock: ${escapeHtml(p.stock ?? 0)}</span><span>$${Number(p.precio || 0).toLocaleString("es-CO")}</span></div>
      <div class="row-actions">
       <button class="btn-primary tiny" type="button" onclick="reservarProductoCarrito(${p.id_producto})">Reservar</button>
       <button class="btn-secondary tiny" type="button" onclick="crearPedidoProducto(${p.id_producto})">Crear pedido</button>
      </div>
    </div>
  </article>`).join("");
}

async function crearPedidoProducto(idProducto) {
  const producto = productosUsuarioCache.find(p => Number(p.id_producto) === Number(idProducto));
  if (!producto) {
    showToast("Producto no encontrado. Actualiza la tienda e intenta de nuevo.", "error");
    return;
  }
  const cantidad = await pedirCantidadProducto(producto);
  if (!cantidad) return;
  const total = Number(producto.precio || 0) * cantidad;
  try {
    const usuario = getUsuario();

    const pedido = await apiFetch(API_PATHS.pedidos, {
      method: "POST",
      body: JSON.stringify({
        id_usuario: Number(usuario?.id_usuario || usuario?.id),
        id_negocio: Number(carrito.id_negocio),
        total,
        estado: "pendiente"
      })  
    });
    await apiFetch(API_PATHS.pedidoDetalle, {
      method: "POST",
      body: JSON.stringify({
        id_pedido: pedido.id_pedido,
        id_producto: Number(idProducto),
        cantidad,
        precio_unitario: Number(producto.precio || 0),
        subtotal: total
      })
    }).catch(() => null);
    showToast(`Pedido #${pedido.id_pedido} creado por $${total.toLocaleString("es-CO")}.`, "success", 6200);
    await irMisPedidos();
  } catch (e) { showToast(friendlyError(e), "error"); }
}
async function reservarProductoCarrito(idProducto) {
  const producto = productosUsuarioCache.find(p => Number(p.id_producto) === Number(idProducto));

  if (!producto) {
    showToast("Producto no encontrado. Actualiza la tienda e intenta de nuevo.", "error");
    return;
  }

  const cantidad = await pedirCantidadProducto(producto);
  if (!cantidad) return;

  try {
    const carrito = await apiFetch("/carritos/agregar-producto", {
      method: "POST",
      body: JSON.stringify({
        id_producto: Number(idProducto),
        cantidad: Number(cantidad)
      })
    });

    showToast(
      `Producto reservado en el carrito. Total actual: $${Number(carrito.total_estimado || 0).toLocaleString("es-CO")}`,
      "success",
      6500
    );

    await cargarProductosUsuario();

  } catch (e) {
    showToast(friendlyError(e), "error");
  }
}
async function continuarCarritoAPedido() {
  try {
    const data = await apiFetch("/carritos/activo/detalle");

    const carrito = data?.carrito;
    const items = Array.isArray(data?.items) ? data.items : [];

    if (!carrito || !items.length) {
      showToast("Tu carrito está vacío o las reservas vencieron.", "info");
      await cargarCarritoUsuario();
      return;
    }

    const total = Number(carrito.total_estimado || 0);

    if (total <= 0) {
      showToast("El carrito no tiene total válido para crear pedido.", "error");
      await cargarCarritoUsuario();
      return;
    }

    const usuario = getUsuario();

    const idUsuarioPedido = Number(
      carrito.id_usuario ||
      usuario?.id_usuario ||
      usuario?.id    
    );

    if (!idUsuarioPedido) {
      showToast("No se pudo identificar el usuario del pedido. Inicia sesión nuevamente.", "error");
      return;
    }

    const pedido = await apiFetch(API_PATHS.pedidos, {
      method: "POST",
      body: JSON.stringify({
        id_usuario: idUsuarioPedido,
        id_negocio: Number(carrito.id_negocio),
        total,
        estado: "pendiente"
      })
    });
    for (const item of items) {
      await apiFetch(API_PATHS.pedidoDetalle, {
        method: "POST",
        body: JSON.stringify({
          id_pedido: pedido.id_pedido,
          tipo_item: item.tipo_item || "producto",
          id_producto: item.id_producto ? Number(item.id_producto) : null,
          id_servicio: item.id_servicio ? Number(item.id_servicio) : null,
          cantidad: Number(item.cantidad || 1),
          precio_unitario: Number(item.precio_unitario || 0),
          subtotal: Number(item.subtotal || 0)
        })
      });
    }
    await apiFetch(`/carritos/${carrito.id_carrito}/convertir`, {
      method: "POST"
    });
    showToast(
      `Pedido #${pedido.id_pedido} creado correctamente. Ahora puedes pagarlo.`,
      "success",
      6500
    );

    await irMisPedidos();

  } catch (e) {
    showToast(friendlyError(e), "error");
  }
}
async function irCarritoUsuario() {
  mostrarModuloCliente("carrito-usuario");
  await cargarCarritoUsuario();
}

async function cargarCarritoUsuario() {
  const cont = document.getElementById("listaCarritoUsuario");
  const totalEl = document.getElementById("carritoTotalUsuario");

  if (cont) {
    cont.innerHTML = `<div class="empty-state">Cargando carrito...</div>`;
  }

  try {
    const data = await apiFetch("/carritos/activo/detalle");
    renderCarritoUsuario(data);
  } catch (e) {
    if (cont) {
      cont.innerHTML = `<div class="empty-state">${escapeHtml(friendlyError(e))}</div>`;
    }

    if (totalEl) {
      totalEl.textContent = "$0";
    }
  }
}

function renderCarritoUsuario(data) {
  const cont = document.getElementById("listaCarritoUsuario");
  const totalEl = document.getElementById("carritoTotalUsuario");

  if (!cont) return;

  const carrito = data?.carrito;
  const items = Array.isArray(data?.items) ? data.items : [];

  if (!carrito || !items.length) {
    cont.innerHTML = `<div class="empty-state">Tu carrito está vacío o las reservas vencieron.</div>`;
    if (totalEl) totalEl.textContent = "$0";
    return;
  }

  if (totalEl) {
    totalEl.textContent = `$${Number(carrito.total_estimado || 0).toLocaleString("es-CO")}`;
  }

  cont.innerHTML = items.map(item => `
    <article class="admin-item">
      <div>
        <h4>${escapeHtml(item.nombre || "Producto")}</h4>
        <p>
          Cantidad: ${escapeHtml(item.cantidad || 0)}
          · Precio: $${Number(item.precio_unitario || 0).toLocaleString("es-CO")}
          · Subtotal: $${Number(item.subtotal || 0).toLocaleString("es-CO")}
        </p>
        <span class="status-pill pending">
          Reserva hasta ${escapeHtml(formatearFechaCorta(item.fecha_expiracion_reserva))}
        </span>
      </div>
    </article>
  `).join("");
}
async function irMisPedidos() {
  mostrarModuloCliente("mis-pedidos-usuario");
  await cargarMisPedidos();
}

async function cargarMisPedidos() {
  const cont = document.getElementById("listaMisPedidos");
  try {
    const [pedidos, pagos] = await Promise.all([
      apiFetch(API_PATHS.pedidos),
      apiFetch(API_PATHS.pagos).catch(() => [])
    ]);
    misPedidosCache = Array.isArray(pedidos) ? pedidos : [];
    misPagosCache = Array.isArray(pagos) ? pagos : [];
    renderMisPedidos();
    mostrarMensaje("misPedidosMsg", "", false);
  } catch (e) {
    if (cont) cont.innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
  }
}

function pedidoPagado(idPedido) {
  return misPagosCache.some(p => Number(p.id_pedido) === Number(idPedido) && !String(p.estado_pago || "").toLowerCase().includes("rechaz"));
}

function renderMisPedidos() {
  const cont = document.getElementById("listaMisPedidos");
  if (!cont) return;
  if (!misPedidosCache.length) {
    cont.innerHTML = `<div class="empty-state">Todavía no tienes pedidos.</div>`;
    return;
  }
  cont.innerHTML = misPedidosCache.map(p => {
    const pagado = pedidoPagado(p.id_pedido);
    return `<article class="admin-item">
      <div>
        <h4>Pedido #${escapeHtml(p.id_pedido)}</h4>
        <p>${escapeHtml(negocioNombrePorId(p.id_negocio))} · Total: $${Number(p.total || 0).toLocaleString("es-CO")} · Estado: ${escapeHtml(p.estado || "pendiente")}</p>
        <span class="status-pill ${pagado ? 'done' : 'pending'}">${pagado ? 'Pago registrado' : 'Pago pendiente'}</span>
      </div>
      <div class="row-actions">
        ${pagado ? `
          <button onclick="descargarFacturaPedido(${p.id_pedido})">Descargar factura</button>
          <button onclick="imprimirFacturaPedido(${p.id_pedido})">Imprimir factura</button>
        ` : `<button onclick="pagarPedido(${p.id_pedido})">Pagar pedido</button>`}
      </div>
    </article>`;
  }).join("");
}

async function obtenerFacturaPorPedido(idPedido) {
  const facturas = await apiFetch("/facturas/");
  const factura = Array.isArray(facturas)
    ? facturas.find(f => Number(f.id_pedido) === Number(idPedido))
    : null;

  if (!factura) {
    throw new Error("No se encontró factura para este pedido.");
  }

  return factura;
}

async function descargarFacturaPedido(idPedido) {
  try {
    const factura = await obtenerFacturaPorPedido(idPedido);
    const token = getToken();
    const url = `${API_BASE}/facturas/${factura.id_factura}/pdf`;

    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (!res.ok) {
      throw new Error("No se pudo descargar la factura.");
    }

    const blob = await res.blob();
    const fileUrl = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = fileUrl;
    link.download = factura.nombre_archivo_pdf || `${factura.numero_factura || "factura"}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(fileUrl);
  } catch (e) {
    showToast(friendlyError(e), "error");
  }
}

async function imprimirFacturaPedido(idPedido) {
  try {
    const factura = await obtenerFacturaPorPedido(idPedido);
    const token = getToken();
    const url = `${API_BASE}/facturas/${factura.id_factura}/pdf`;

    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (!res.ok) {
      throw new Error("No se pudo abrir la factura para imprimir.");
    }

    const blob = await res.blob();
    const fileUrl = URL.createObjectURL(blob);

    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = fileUrl;
    document.body.appendChild(iframe);

    iframe.onload = () => {
      iframe.contentWindow.focus();
      iframe.contentWindow.print();
    };

    setTimeout(() => {
      URL.revokeObjectURL(fileUrl);
    }, 60000);
  } catch (e) {
    showToast(friendlyError(e), "error");
  }
}

async function pagarPedido(idPedido) {
  const pedido = misPedidosCache.find(p => Number(p.id_pedido) === Number(idPedido));
  if (!pedido) {
    showToast("Pedido no encontrado. Actualiza tus pedidos e intenta nuevamente.", "error");
    return;
  }
  const result = await openUiModal({
    eyebrow: "Pagos",
    title: "Registrar pago",
    text: `Pedido #${idPedido}. Total a registrar: $${Number(pedido.total || 0).toLocaleString("es-CO")}.`,
    confirmText: "Registrar pago",
    fields: [
      { id: "metodo", label: "Método de pago", type: "select", value: "efectivo", options: [
        { value: "efectivo", label: "Efectivo" },
        { value: "transferencia", label: "Transferencia" },
        { value: "tarjeta", label: "Tarjeta" },
      ]},
      { id: "referencia", label: "Referencia opcional", type: "text", value: `PED-${idPedido}-${Date.now()}`, required: false },
      { id: "correo_factura", label: "Correo para factura (opcional)", type: "email", value: "", required: false }
    ]
  });
  if (!result) return;
  try {
    await apiFetch(API_PATHS.pagos, {
      method: "POST",
      body: JSON.stringify({
        id_pedido: Number(idPedido),
        metodo_pago: result.metodo || "efectivo",
        referencia_externa: result.referencia || `PED-${idPedido}-${Date.now()}`,
        estado_pago: "aprobado",
        valor: Number(pedido.total || 0),
        respuesta_pasarela: "Pago registrado desde front",
        correo_factura: result.correo_factura || null
      })
    });
    showToast("Pago registrado correctamente.", "success");
    await cargarMisPedidos();
  } catch (e) { showToast(friendlyError(e), "error"); }
}


document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("empleadoForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const idEditar = document.getElementById("empId")?.value;
    const payload = {
      nombre: document.getElementById("empNombre").value.trim(),
      apellido: document.getElementById("empApellido").value.trim(),
      telefono: document.getElementById("empTelefono").value.trim() || null,
      email: document.getElementById("empEmail").value.trim() || null,
      especialidad: document.getElementById("empEspecialidad").value.trim() || null,
      foto_url: document.getElementById("empFoto").value.trim() || null,
    };
    if (payload.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(payload.email)) {
      mostrarMensaje("empleadoMsg", "El correo del empleado no es válido. Ejemplo: empleado@gmail.com");
      return;
    }

    try {
      if (idEditar) {
        await apiFetch(`${API_PATHS.empleados}${idEditar}`, { method: "PUT", body: JSON.stringify(payload) });
        mostrarMensaje("empleadoMsg", "Empleado actualizado correctamente.", false);
        cancelarEdicionEmpleado(false);
      } else {
        const idNegocio = await obtenerIdNegocioActual();
        await apiFetch(API_PATHS.empleados, {
          method: "POST",
          body: JSON.stringify({ ...payload, id_negocio: idNegocio })
        });
        e.target.reset();
        mostrarMensaje("empleadoMsg", "Empleado creado correctamente.", false);
      }
      cargarEmpleados();
    } catch (err) {
      mostrarMensaje("empleadoMsg", err.message);
    }
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
    try {
      const idNegocio = await obtenerIdNegocioActual();
      await apiFetch(API_PATHS.servicios, {
        method: "POST",
        body: JSON.stringify({ ...payload, id_negocio: idNegocio })
      });
      e.target.reset();
      mostrarMensaje("servicioMsg", "Servicio creado correctamente.", false);
      cargarServicios();
    }
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
    try {
      const idNegocio = await obtenerIdNegocioActual();
      await apiFetch(API_PATHS.productos, {
        method: "POST",
        body: JSON.stringify({ ...payload, id_negocio: idNegocio })
      });
      e.target.reset();
      mostrarMensaje("productoMsg", "Producto creado correctamente.", false);
      showToast("Producto creado correctamente.", "success");
      cargarProductos();
    }
    catch (err) { const msg = friendlyError(err); mostrarMensaje("productoMsg", msg); showToast(msg, "error"); }
  });

  document.getElementById("btnMfaSetup")?.addEventListener("click", iniciarConfiguracionMFA);

  document.getElementById("mfaConfirmForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    await confirmarConfiguracionMFA();
  });

  document.getElementById("agendarCitaForm")?.addEventListener("submit", agendarCitaCliente);
  document.getElementById("citaEmpleado")?.addEventListener("change", (e) => cargarHorariosEmpleadoCliente(Number(e.target.value)));
  document.getElementById("citaServicio")?.addEventListener("change", actualizarOpcionesHoraDisponible);
  document.getElementById("citaFecha")?.addEventListener("change", actualizarOpcionesHoraDisponible);

  document.getElementById("horarioEmpleadoForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const idEmpleado = Number(document.getElementById("horarioEmpleadoSelect").value);
    const dias = diasSeleccionadosHorario();
    const payloadBase = {
      id_empleado: idEmpleado,
      hora_inicio: normalizarHoraApi(document.getElementById("horarioInicio").value),
      hora_fin: normalizarHoraApi(document.getElementById("horarioFin").value),
      disponible: document.getElementById("horarioDisponible").checked,
    };

    if (!payloadBase.id_empleado || !dias.length || !payloadBase.hora_inicio || !payloadBase.hora_fin) {
      mostrarMensaje("horarioMsg", "Completa empleado, al menos un día, hora de inicio y hora de fin.");
      return;
    }

    try {
      for (const dia of dias) {
        await apiFetchConRutas(RUTAS_HORARIOS, {
          method: "POST",
          body: JSON.stringify({ ...payloadBase, dia_semana: dia })
        });
      }
      e.target.reset();
      limpiarDiasHorario();
      mostrarMensaje("horarioMsg", `Horario guardado para ${dias.length} día(s).`, false);
      cargarHorariosEmpleadoSeleccionado();
    } catch (err) {
      mostrarMensaje("horarioMsg", err.message);
    }
  });
});

function ponerEmpleadoEnFormulario(empleado) {
  document.getElementById("empId").value = empleado.id_empleado || "";
  document.getElementById("empNombre").value = empleado.nombre || "";
  document.getElementById("empApellido").value = empleado.apellido || "";
  document.getElementById("empTelefono").value = empleado.telefono || "";
  document.getElementById("empEmail").value = empleado.email || "";
  document.getElementById("empEspecialidad").value = empleado.especialidad || "";
  document.getElementById("empFoto").value = empleado.foto_url || "";
  const title = document.getElementById("empleadoFormTitle");
  const btn = document.getElementById("empleadoSubmitBtn");
  const cancel = document.getElementById("empleadoCancelEditBtn");
  if (title) title.textContent = "Editar empleado";
  if (btn) btn.textContent = "Actualizar empleado";
  if (cancel) cancel.style.display = "inline-flex";
  document.getElementById("empNombre")?.focus();
}

function cancelarEdicionEmpleado(limpiarMensaje = true) {
  const form = document.getElementById("empleadoForm");
  if (form) form.reset();
  const id = document.getElementById("empId");
  if (id) id.value = "";
  const title = document.getElementById("empleadoFormTitle");
  const btn = document.getElementById("empleadoSubmitBtn");
  const cancel = document.getElementById("empleadoCancelEditBtn");
  if (title) title.textContent = "Crear empleado";
  if (btn) btn.textContent = "Guardar empleado";
  if (cancel) cancel.style.display = "none";
  if (limpiarMensaje) mostrarMensaje("empleadoMsg", "", false);
}

async function editarEmpleado(id) {
  let empleado = empleadosCache.find(e => Number(e.id_empleado) === Number(id));
  try {
    if (!empleado) empleado = await apiFetch(`${API_PATHS.empleados}${id}`);
    ponerEmpleadoEnFormulario(empleado);
  } catch (e) {
    showToast(friendlyError(e), "error");
  }
}
async function eliminarEmpleado(id) {
  const ok = await pedirConfirmacion({
    title: "Eliminar empleado",
    text: "También se eliminarán sus horarios y citas asociadas. Esta acción no se puede deshacer fácilmente.",
    confirmText: "Eliminar empleado",
    danger: true
  });
  if (!ok) return;
  try { await apiFetch(`${API_PATHS.empleados}${id}`, { method: "DELETE" }); showToast("Empleado eliminado correctamente.", "success"); cargarEmpleados(); }
  catch (e) { showToast(friendlyError(e), "error"); }
}
async function editarServicio(id) {
  const servicio = serviciosCache?.find?.(s => Number(s.id_servicio) === Number(id));
  const precio = await pedirPrecioNuevo("Actualizar precio del servicio", servicio?.precio ?? "");
  if (precio === null) return;
  try { await apiFetch(`${API_PATHS.servicios}${id}`, { method: "PUT", body: JSON.stringify({ precio }) }); showToast("Precio del servicio actualizado.", "success"); cargarServicios(); }
  catch (e) { showToast(friendlyError(e), "error"); }
}
async function eliminarServicio(id) {
  const ok = await pedirConfirmacion({ title: "Eliminar o desactivar servicio", text: "El servicio dejará de estar disponible para agendar nuevas citas.", confirmText: "Continuar", danger: true });
  if (!ok) return;
  try { await apiFetch(`${API_PATHS.servicios}${id}`, { method: "DELETE" }); showToast("Servicio actualizado correctamente.", "success"); cargarServicios(); }
  catch (e) { showToast(friendlyError(e), "error"); }
}
async function editarProducto(id) {
  const producto = productosCache?.find?.(p => Number(p.id_producto) === Number(id));
  const precio = await pedirPrecioNuevo("Actualizar precio del producto", producto?.precio ?? "");
  if (precio === null) return;
  try { await apiFetch(`${API_PATHS.productos}${id}`, { method: "PUT", body: JSON.stringify({ precio }) }); showToast("Precio del producto actualizado.", "success"); cargarProductos(); }
  catch (e) { showToast(friendlyError(e), "error"); }
}
async function eliminarProducto(id) {
  const ok = await pedirConfirmacion({ title: "Desactivar producto", text: "El producto dejará de estar disponible en la tienda.", confirmText: "Desactivar", danger: true });
  if (!ok) return;
  try { await apiFetch(`${API_PATHS.productos}${id}`, { method: "DELETE" }); showToast("Producto desactivado correctamente.", "success"); cargarProductos(); }
  catch (e) { showToast(friendlyError(e), "error"); }
}
async function movimientoInventario(id) {
  const result = await openUiModal({
    eyebrow: "Inventario",
    title: "Registrar movimiento",
    text: "Registra una entrada o salida de inventario con un motivo claro.",
    confirmText: "Guardar movimiento",
    fields: [
      { id: "tipo_movimiento", label: "Tipo de movimiento", type: "select", value: "entrada", options: [
        { value: "entrada", label: "Entrada" },
        { value: "salida", label: "Salida" }
      ]},
      { id: "cantidad", label: "Cantidad", type: "number", min: 1, step: 1, value: 1 },
      { id: "motivo", label: "Motivo", type: "textarea", value: "Ajuste manual", required: false }
    ]
  });
  if (!result) return;
  const cantidad = Number(result.cantidad);
  if (!Number.isInteger(cantidad) || cantidad < 1) {
    showToast("Ingresa una cantidad válida mayor a cero.", "error");
    return;
  }
  try {
    await apiFetch(API_PATHS.inventario, { method: "POST", body: JSON.stringify({ id_producto: id, tipo_movimiento: result.tipo_movimiento, cantidad, motivo: result.motivo || "Ajuste manual" }) });
    showToast("Movimiento de inventario registrado.", "success");
    cargarProductos();
  } catch (e) { showToast(friendlyError(e), "error"); }
}
async function cancelarCita(id) {
  const ok = await pedirConfirmacion({ title: "Cancelar cita", text: "La cita será cancelada para el negocio y el usuario.", confirmText: "Cancelar cita", danger: true });
  if (!ok) return;
  try { await apiFetchConRutas([`/citas/${id}`, `/cita/${id}`], { method: "DELETE" }); showToast("Cita cancelada correctamente.", "success"); cargarCitas(); }
  catch (e) { showToast(friendlyError(e), "error"); }
}


window.addEventListener("focus", () => {
  if (getToken()) validarSesionActiva({ silencioso: true });
});

document.addEventListener("visibilitychange", () => {
  if (!document.hidden && getToken()) validarSesionActiva({ silencioso: true });
});
function irGestionUsuarios() {
  setVisible(["gestion-usuarios-admin"]);
  cargarUsuariosAdmin();
}
function irAuditoriaSistema() {
  setVisible(["auditoria-admin"]);
  cargarResumenAuditoriaGeneral();
  cargarAuditoriaAdmin();
}

function limpiarFiltrosAuditoria() {
  const campos = [
    "auditoriaCorreo",
    "auditoriaAccion",
    "auditoriaModulo",
    "auditoriaResultado",
    "auditoriaNivel"
  ];

  campos.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = "";
  });

  const limite = document.getElementById("auditoriaLimite");
  if (limite) limite.value = 50;

  cargarAuditoriaAdmin();
}
let auditoriaAdminCache = [];

async function cargarAuditoriaAdmin() {
  const contenedor = document.getElementById("tablaAuditoriaAdmin");
  const msg = document.getElementById("auditoriaAdminMsg");

  if (!contenedor) return;

  contenedor.innerHTML = "<p class='muted'>Cargando auditoría...</p>";
  if (msg) msg.textContent = "";

  const correo = document.getElementById("auditoriaCorreo")?.value.trim();
  const accion = document.getElementById("auditoriaAccion")?.value.trim();
  const modulo = document.getElementById("auditoriaModulo")?.value.trim();
  const resultado = document.getElementById("auditoriaResultado")?.value;
  const nivel = document.getElementById("auditoriaNivel")?.value;
  const limite = document.getElementById("auditoriaLimite")?.value || 50;

  const params = new URLSearchParams();

  if (correo) params.append("correo_usuario", correo);
  if (accion) params.append("accion", accion);
  if (modulo) params.append("modulo", modulo);
  if (resultado) params.append("resultado", resultado);
  if (nivel) params.append("nivel", nivel);
  if (limite) params.append("limite", limite);

  try {
    const data = await apiFetch(`/auditoria/?${params.toString()}`);
    auditoriaAdminCache = Array.isArray(data) ? data : [];
    renderAuditoriaAdmin(auditoriaAdminCache);

  } catch (error) {
  contenedor.innerHTML = "<p class='muted'>No se pudo cargar la auditoría.</p>";
  if (msg) msg.textContent = friendlyError(error);
  showToast(friendlyError(error), "error");
}}

function renderAuditoriaAdmin(registros) {
  const contenedor = document.getElementById("tablaAuditoriaAdmin");
  if (!contenedor) return;

  if (!Array.isArray(registros) || registros.length === 0) {
    contenedor.innerHTML = "<p class='muted'>No hay registros de auditoría para mostrar.</p>";
    return;
  }

 contenedor.innerHTML = registros.map((item) => `
   <div class="admin-table-row auditoria-row">
     <span>${formatearFechaAuditoria(item.fecha_hora || item.fecha || item.created_at)}</span>
     <span>${item.correo_usuario || "—"}</span>
     <span>${item.rol_usuario || "—"}</span>
     <span>${item.accion || "—"}</span>
     <span>${item.modulo || "—"}</span>
     <span>${item.tabla_afectada || item.tabla || "—"}</span>
     <span>${badgeAuditoria(item.resultado, "resultado")}</span>
     <span>${badgeAuditoria(item.nivel, "nivel")}</span>
     <span>
       <button 
         type="button" 
         class="btn-detalle-auditoria"
         onclick="abrirDetalleAuditoria('${encodeURIComponent(JSON.stringify(item))}')">
         Ver detalle
       </button>
     </span>
   </div>
 `).join("");
}
function badgeAuditoria(valor, tipo = "") {
  const texto = String(valor || "—").toUpperCase();
  const clase = texto
    .replaceAll(" ", "-")
    .replaceAll("_", "-")
    .toLowerCase();

  return `<span class="audit-badge ${tipo}-${clase}">${escapeHtml(texto)}</span>`;
}

function detalleCortoAuditoria(detalle) {
  const texto = String(detalle || "—");
  if (texto.length <= 80) return escapeHtml(texto);
  return `${escapeHtml(texto.slice(0, 80))}...`;
}
function detalleCortoAuditoria(detalle) {
  const texto = String(detalle || "—");
  if (texto.length <= 80) return escapeHtml(texto);
  return `${escapeHtml(texto.slice(0, 80))}...`;
}
function abrirDetalleAuditoria(itemCodificado) {
  let item = {};

  try {
    item = JSON.parse(decodeURIComponent(itemCodificado));
  } catch (error) {
    mostrarToast("No se pudo abrir el detalle de auditoría.", "error");
    return;
  }

  const modal = document.getElementById("modalDetalleAuditoria");
  const contenido = document.getElementById("contenidoDetalleAuditoria");

  if (!modal || !contenido) return;

  const filas = [
    ["Fecha", formatearFechaAuditoria(item.fecha_hora || item.fecha || item.created_at)],
    ["Usuario", item.correo_usuario || "—"],
    ["Rol", item.rol_usuario || "—"],
    ["Acción", item.accion || "—"],
    ["Módulo", item.modulo || "—"],
    ["Tabla", item.tabla_afectada || item.tabla || "—"],
    ["Resultado", item.resultado || "—"],
    ["Nivel", item.nivel || "—"],
    ["Método HTTP", item.metodo_http || "—"],
    ["Ruta", item.ruta || "—"],
    ["IP", item.ip || "—"],
    ["User Agent", item.user_agent || "—"],
    ["Detalle", item.detalle || "—"]
  ];

  contenido.innerHTML = filas.map(([titulo, valor]) => `
    <div class="modal-auditoria-item">
      <strong>${escapeHtml(titulo)}</strong>
      <span>${escapeHtml(valor)}</span>
    </div>
  `).join("");

  modal.style.display = "flex";
  document.body.classList.add("modal-open");
}

function cerrarDetalleAuditoria() {
  const modal = document.getElementById("modalDetalleAuditoria");
  if (modal) modal.style.display = "none";
  document.body.classList.remove("modal-open");
}
function actualizarResumenAuditoria(registros) {
  const total = registros.length;
  const ok = registros.filter(r => (r.resultado || "").toUpperCase() === "OK").length;
  const error = registros.filter(r => (r.resultado || "").toUpperCase() === "ERROR").length;
  const warn = registros.filter(r => (r.nivel || "").toUpperCase() === "WARN").length;

  document.getElementById("auditTotal").textContent = total;
  document.getElementById("auditOk").textContent = ok;
  document.getElementById("auditError").textContent = error;
  document.getElementById("auditWarn").textContent = warn;
}

function formatearFechaAuditoria(valor) {
  if (!valor) return "—";

  try {
    const fecha = new Date(valor);
    if (Number.isNaN(fecha.getTime())) return valor;
    return fecha.toLocaleString("es-CO");
  } catch {
    return valor;
  }
}
let chartAuditoriaResultados = null;
let chartAuditoriaNiveles = null;
let chartAuditoriaAcciones = null;
let chartAuditoriaModulos = null;

async function cargarResumenAuditoriaGeneral() {
  try {
    const data = await apiFetch("/auditoria/?limite=200");
    const registros = Array.isArray(data) ? data : [];

    actualizarResumenAuditoria(registros);
    renderGraficasAuditoriaGeneral(registros);

  } catch (error) {
    showToast("No se pudo cargar el resumen general de auditoría.", "error");
  }
}

function actualizarResumenAuditoria(registros) {
  const lista = Array.isArray(registros) ? registros : [];

  const total = lista.length;
  const ok = lista.filter(r => String(r.resultado || "").toUpperCase() === "OK").length;
  const error = lista.filter(r => String(r.resultado || "").toUpperCase() === "ERROR").length;
  const warn = lista.filter(r => String(r.nivel || "").toUpperCase() === "WARN").length;

  const totalEl = document.getElementById("auditTotal");
  const okEl = document.getElementById("auditOk");
  const errorEl = document.getElementById("auditError");
  const warnEl = document.getElementById("auditWarn");

  if (totalEl) totalEl.textContent = total;
  if (okEl) okEl.textContent = ok;
  if (errorEl) errorEl.textContent = error;
  if (warnEl) warnEl.textContent = warn;
}

function contarPorCampo(registros, campo) {
  const conteo = {};

  registros.forEach(item => {
    const valor = String(item[campo] || "SIN_DATO").toUpperCase();
    conteo[valor] = (conteo[valor] || 0) + 1;
  });

  return conteo;
}

function renderGraficasAuditoriaGeneral(registros) {
  if (typeof Chart === "undefined") {
    console.warn("Chart.js no está cargado.");
    return;
  }

  const resultados = contarPorCampo(registros, "resultado");
  const niveles = contarPorCampo(registros, "nivel");
  const topAcciones = obtenerTopPorCampo(registros, "accion", 6);
  const topModulos = obtenerTopPorCampo(registros, "modulo", 6);

  const ctxResultados = document.getElementById("chartAuditoriaResultados");
  const ctxNiveles = document.getElementById("chartAuditoriaNiveles");
  const ctxAcciones = document.getElementById("chartAuditoriaAcciones");
  const ctxModulos = document.getElementById("chartAuditoriaModulos");

  if (!ctxResultados || !ctxNiveles) return;

  if (chartAuditoriaResultados) chartAuditoriaResultados.destroy();
  if (chartAuditoriaNiveles) chartAuditoriaNiveles.destroy();
  if (chartAuditoriaAcciones) chartAuditoriaAcciones.destroy();
  if (chartAuditoriaModulos) chartAuditoriaModulos.destroy();

  const coloresResultado = {
    OK: "#d4af37",
    ERROR: "#c94c4c",
    PENDIENTE: "#d98e04",
    SIN_DATO: "#6b7280"
  };

  const coloresNivel = {
    INFO: "#d4af37",
    WARN: "#d98e04",
    WARNING: "#d98e04",
    ERROR: "#c94c4c",
    SIN_DATO: "#6b7280"
  };

  const labelsResultados = Object.keys(resultados);
  const dataResultados = Object.values(resultados);
  const backgroundResultados = labelsResultados.map(label => coloresResultado[label] || "#6b7280");

  const labelsNiveles = Object.keys(niveles);
  const dataNiveles = Object.values(niveles);
  const backgroundNiveles = labelsNiveles.map(label => coloresNivel[label] || "#6b7280");

  const opcionesDona = {
    responsive: true,
    maintainAspectRatio: true,
    devicePixelRatio: 2,
    cutout: "52%",
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          color: "#f5f1df",
          padding: 16,
          boxWidth: 18,
          font: {
            family: "Montserrat",
            size: 13,
            weight: "600"
          }
        }
      },
      tooltip: {
        titleFont: {
          family: "Montserrat",
          size: 13,
          weight: "700"
        },
        bodyFont: {
          family: "Montserrat",
          size: 13
        }
      }
    }
  };

  const opcionesBarras = {
    responsive: true,
    maintainAspectRatio: false,
    devicePixelRatio: 2,
    indexAxis: "y",
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        titleFont: {
          family: "Montserrat",
          size: 13,
          weight: "700"
        },
        bodyFont: {
          family: "Montserrat",
          size: 13
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: "#f5f1df",
          font: {
            family: "Montserrat",
            size: 12,
            weight: "600"
          }
        },
        grid: {
          color: "rgba(255,255,255,0.08)"
        }
      },
      y: {
        ticks: {
          color: "#f5f1df",
          font: {
            family: "Montserrat",
            size: 12,
            weight: "600"
          }
        },
        grid: {
          color: "rgba(255,255,255,0.04)"
        }
      }
    }
  };

  chartAuditoriaResultados = new Chart(ctxResultados, {
    type: "doughnut",
    data: {
      labels: labelsResultados,
      datasets: [{
        data: dataResultados,
        backgroundColor: backgroundResultados,
        borderColor: "#111",
        borderWidth: 2,
        hoverOffset: 8
      }]
    },
    options: opcionesDona
  });

  chartAuditoriaNiveles = new Chart(ctxNiveles, {
    type: "doughnut",
    data: {
      labels: labelsNiveles,
      datasets: [{
        data: dataNiveles,
        backgroundColor: backgroundNiveles,
        borderColor: "#111",
        borderWidth: 2,
        hoverOffset: 8
      }]
    },
    options: opcionesDona
  });

  if (ctxAcciones) {
    chartAuditoriaAcciones = new Chart(ctxAcciones, {
      type: "bar",
      data: {
        labels: topAcciones.labels,
        datasets: [{
          data: topAcciones.values,
          backgroundColor: "#d4af37",
          borderColor: "#e8c97a",
          borderWidth: 1,
          borderRadius: 8
        }]
      },
      options: opcionesBarras
    });
  }

  if (ctxModulos) {
    chartAuditoriaModulos = new Chart(ctxModulos, {
      type: "bar",
      data: {
        labels: topModulos.labels,
        datasets: [{
          data: topModulos.values,
          backgroundColor: "#bfa14a",
          borderColor: "#e8c97a",
          borderWidth: 1,
          borderRadius: 8
        }]
      },
      options: opcionesBarras
    });
  }
}
function obtenerTopPorCampo(registros, campo, limite = 6) {
  const conteo = contarPorCampo(registros, campo);

  const ordenado = Object.entries(conteo)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limite);

  return {
    labels: ordenado.map(([label]) => label),
    values: ordenado.map(([, value]) => value)
  };
}
function cargarResumenAdmin() {
  mostrarToast("Resumen administrativo actualizado.", "success");
}
function finalizarCargaDashboard() {
  document.body.classList.remove("dashboard-loading");

  const loader = document.getElementById("appLoader");
  if (loader) {
    loader.style.display = "none";
  }
}
let usuariosAdminCache = [];

function mostrarDashboardAdmin() {
  setVisible(["dashboard-admin"]);
}

async function cargarUsuariosAdmin() {
  const contenedor = document.getElementById("tablaUsuariosAdmin");
  const msg = document.getElementById("usuariosAdminMsg");

  if (!contenedor) return;

  contenedor.innerHTML = "<p class='muted'>Cargando usuarios...</p>";
  if (msg) msg.textContent = "";

  try {
    const data = await apiRequest("/auth/usuarios");

    usuariosAdminCache = Array.isArray(data) ? data : [];
    renderUsuariosAdmin(usuariosAdminCache);

  } catch (error) {
    contenedor.innerHTML = "<p class='muted'>No se pudieron cargar los usuarios.</p>";
    if (msg) msg.textContent = obtenerMensajeError(error);
  }
}

function renderUsuariosAdmin(usuarios) {
  const contenedor = document.getElementById("tablaUsuariosAdmin");
  if (!contenedor) return;

  if (!usuarios.length) {
    contenedor.innerHTML = "<p class='muted'>No hay usuarios registrados.</p>";
    return;
  }

  contenedor.innerHTML = usuarios.map((usuario) => `
    <div class="admin-table-row">
      <span>${usuario.id_usuario}</span>
      <span>${usuario.nombre || ""} ${usuario.apellido || ""}</span>
      <span>${usuario.correo || ""}</span>
      <span>
        <select onchange="cambiarRolUsuarioAdmin(${usuario.id_usuario}, this.value)">
          <option value="cliente" ${usuario.rol === "cliente" ? "selected" : ""}>cliente</option>
          <option value="negocio" ${usuario.rol === "negocio" ? "selected" : ""}>negocio</option>
          <option value="admin" ${usuario.rol === "admin" ? "selected" : ""}>admin</option>
          <option value="superadmin" ${usuario.rol === "superadmin" ? "selected" : ""}>superadmin</option>
        </select>
      </span>
      <span>${usuario.estado || ""}</span>
      <span>
        <button class="btn-danger small" onclick="eliminarUsuarioAdmin(${usuario.id_usuario})">
          Eliminar
        </button>
      </span>
    </div>
  `).join("");
}

function filtrarUsuariosAdmin() {
  const input = document.getElementById("buscarUsuarioAdmin");
  const texto = (input?.value || "").toLowerCase().trim();

  if (!texto) {
    renderUsuariosAdmin(usuariosAdminCache);
    return;
  }

  const filtrados = usuariosAdminCache.filter((usuario) => {
    const plano = `
      ${usuario.id_usuario}
      ${usuario.nombre || ""}
      ${usuario.apellido || ""}
      ${usuario.correo || ""}
      ${usuario.rol || ""}
      ${usuario.estado || ""}
    `.toLowerCase();

    return plano.includes(texto);
  });

  renderUsuariosAdmin(filtrados);
}

async function cambiarRolUsuarioAdmin(idUsuario, nuevoRol) {
  try {
    await apiRequest(`/auth/usuarios/${idUsuario}/rol`, {
      method: "PATCH",
      body: JSON.stringify({ nuevo_rol: nuevoRol })
    });

    mostrarToast("Rol actualizado correctamente.", "success");
    cargarUsuariosAdmin();

  } catch (error) {
    mostrarToast(obtenerMensajeError(error), "error");
    cargarUsuariosAdmin();
  }
}

async function eliminarUsuarioAdmin(idUsuario) {
  const confirmar = window.confirm("¿Seguro que deseas eliminar este usuario? Esta acción no se puede deshacer.");
  if (!confirmar) return;

  try {
    await apiRequest(`/auth/usuarios/${idUsuario}`, {
      method: "DELETE"
    });

    mostrarToast("Usuario eliminado correctamente.", "success");
    cargarUsuariosAdmin();

  } catch (error) {
    mostrarToast(obtenerMensajeError(error), "error");
  }
}
