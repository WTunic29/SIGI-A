// ─────────────────────────────────────────────
// CONFIG
// ─────────────────────────────────────────────
const API_BASE = "https://sigi-a.onrender.com";
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
  "dashboard-negocio", "dashboard-usuario", "dashboard-admin", "mi-perfil",
  "ver-negocios", "validar-acceso", "registrar-negocio",
  "gestion-empleados", "gestion-servicios", "gestion-productos", "gestion-citas", "detalle-negocio",
  "mis-citas-usuario", "mis-calificaciones-usuario", "tienda-usuario", "mis-pedidos-usuario"
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
    if (input) input.placeholder = "Código 2FA";
    if (btn) btn.textContent = "Verificar";
  }
}

function mostrarVerify2FA(tipo = "email") {
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

function irDashboardPorRol() {
  const usuario = getUsuario();
  if (!usuario) return mostrarInicio();

  const rol = normalizarRol(usuario.rol);
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
  if (value === "administrador" || value === "superusuario" || value === "superuser" || value === "super_admin" || value === "super-admin") return "admin";
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
  if (!confirm("¿Eliminar este horario?")) return;
  try {
    await apiFetchConRutas(RUTAS_HORARIOS.map(r => `${r}${idHorario}`), { method: "DELETE" });
    cargarHorariosEmpleadoSeleccionado();
  } catch (e) { alert(e.message); }
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
        mostrarVerify2FA("totp");
        mostrarMensaje("verify2faMsg", "Ingresa el código de tu aplicación autenticadora.", false);
        showToast("Verificación con app autenticadora requerida.", "info");
      } else if (res.ok && data.requieres_2fa) {
        sessionStorage.setItem("correo_2fa", data.correo || payload.correo);
        sessionStorage.setItem("mfa_mode", "email");
        mostrarVerify2FA("email");
        mostrarMensaje("verify2faMsg", "Código enviado a tu correo.", false);
        showToast("Te enviamos un código de seguridad al correo.", "success");
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
  const hash = window.location.hash;

  if (hash === "#login") {
    mostrarLogin();
    return;
  }

  if (hash === "#recuperar-password") {
    mostrarRecuperarPassword();
    return;
  }

  if (!getToken() || !usuario) {
    actualizarNavbar();
    return;
  }

  const sesionOk = await validarSesionActiva();
  if (sesionOk) irDashboardPorRol();
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
  if (!confirm("¿Eliminar este horario?")) return;
  try {
    await apiFetchConRutas(RUTAS_HORARIOS.map(r => `${r}${idHorario}`), { method: "DELETE" });
    cargarHorariosEmpleadoSeleccionado();
  } catch (e) { alert(e.message); }
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
    alert("Esta opción es para cuentas tipo usuario/cliente.");
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
  if (!confirm("¿Cancelar esta cita?")) return;
  try {
    await apiFetch(`${API_PATHS.citas}${idCita}`, { method: "DELETE" });
    await cargarMisCitas();
  } catch (e) { alert(e.message); }
}

async function calificarCita(idCita, idNegocio) {
  const puntuacion = Number(prompt("Puntuación de 1 a 5:", "5"));
  if (!puntuacion) return;
  const comentario = prompt("Comentario:", "Buen servicio") || "";
  try {
    await apiFetch(API_PATHS.calificaciones, {
      method: "POST",
      body: JSON.stringify({ id_negocio: Number(idNegocio), id_cita: Number(idCita), puntuacion, comentario })
    });
    alert("Calificación registrada correctamente.");
    await cargarMisCalificaciones();
  } catch (e) { alert(e.message); }
}

function pagarCitaInfo(idCita) {
  alert(`La cita #${idCita} ya se puede listar y calificar. Para pagar citas directamente falta que el backend de pagos acepte id_cita o que exista una ruta específica de pago de citas. Actualmente /pagos/ está ligado a id_pedido.`);
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
  if (!confirm("¿Eliminar esta calificación?")) return;
  try { await apiFetch(`${API_PATHS.calificaciones}${id}`, { method: "DELETE" }); cargarMisCalificaciones(); }
  catch (e) { alert(e.message); }
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
      <button class="btn-primary tiny" type="button" onclick="crearPedidoProducto(${p.id_producto})">Crear pedido</button>
    </div>
  </article>`).join("");
}

async function crearPedidoProducto(idProducto) {
  const producto = productosUsuarioCache.find(p => Number(p.id_producto) === Number(idProducto));
  if (!producto) return alert("Producto no encontrado.");
  const cantidad = Number(prompt(`Cantidad para ${producto.nombre}:`, "1"));
  if (!cantidad || cantidad < 1) return;
  const total = Number(producto.precio || 0) * cantidad;
  try {
    const pedido = await apiFetch(API_PATHS.pedidos, {
      method: "POST",
      body: JSON.stringify({ id_negocio: Number(producto.id_negocio), total, estado: "pendiente" })
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
    alert(`Pedido #${pedido.id_pedido} creado por $${total.toLocaleString("es-CO")}.`);
    await irMisPedidos();
  } catch (e) { alert(e.message); }
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
        ${pagado ? "" : `<button onclick="pagarPedido(${p.id_pedido})">Pagar pedido</button>`}
      </div>
    </article>`;
  }).join("");
}

async function pagarPedido(idPedido) {
  const pedido = misPedidosCache.find(p => Number(p.id_pedido) === Number(idPedido));
  if (!pedido) return alert("Pedido no encontrado.");
  const metodo = prompt("Método de pago:", "efectivo") || "efectivo";
  const referencia = prompt("Referencia externa opcional:", `PED-${idPedido}-${Date.now()}`) || `PED-${idPedido}-${Date.now()}`;
  try {
    await apiFetch(API_PATHS.pagos, {
      method: "POST",
      body: JSON.stringify({
        id_pedido: Number(idPedido),
        metodo_pago: metodo,
        referencia_externa: referencia,
        estado_pago: "aprobado",
        valor: Number(pedido.total || 0),
        respuesta_pasarela: "Pago registrado desde front"
      })
    });
    alert("Pago registrado correctamente.");
    await cargarMisPedidos();
  } catch (e) { alert(e.message); }
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
    alert(e.message);
  }
}
async function eliminarEmpleado(id) {
  if (!confirm("¿Eliminar este empleado definitivamente? También se eliminarán sus horarios y citas asociadas.")) return;
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
  try { await apiFetchConRutas([`/citas/${id}`, `/cita/${id}`], { method: "DELETE" }); cargarCitas(); }
  catch (e) { alert(e.message); }
}


window.addEventListener("focus", () => {
  if (getToken()) validarSesionActiva({ silencioso: true });
});

document.addEventListener("visibilitychange", () => {
  if (!document.hidden && getToken()) validarSesionActiva({ silencioso: true });
});
