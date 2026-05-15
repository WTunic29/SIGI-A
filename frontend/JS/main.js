// ═══════════════════════════════════════
//  CONFIG
// ═══════════════════════════════════════
const API_BASE = "http://localhost:8000";
const TODAS = [
  "inicio","cta","login","registro","verify2fa",
  "dashboard-negocio","dashboard-cliente",
  "mi-perfil","registrar-negocio",
  "servicios","empleados","productos","citas",
  "mis-citas","ver-negocios","ver-negocios-cliente"
];
const ROLES = { "negocio":"Propietario", "cliente":"Cliente", "admin":"Administrador", "empleado":"Empleado" };
let negocioActual = null;
let todosLosNegocios = [];

// ═══════════════════════════════════════
//  NAVBAR SCROLL
// ═══════════════════════════════════════
const navbar = document.getElementById("navbar");
window.addEventListener("scroll", () => navbar.classList.toggle("scrolled", window.scrollY > 60));

// ═══════════════════════════════════════
//  NAVEGACIÓN
// ═══════════════════════════════════════
function setVisible(show, hide) {
  hide.forEach(id => { const el=document.getElementById(id); if(el) el.style.display="none"; });
  show.forEach(id => {
    const el=document.getElementById(id); if(!el) return;
    const flexIds=["inicio","login","registro","verify2fa","dashboard-negocio","dashboard-cliente","mi-perfil","registrar-negocio","servicios","empleados","productos","citas","mis-citas","ver-negocios","ver-negocios-cliente"];
    el.style.display = flexIds.includes(id) ? "flex" : "block";
  });
  window.scrollTo(0,0);
}
function mostrarInicio()            { setVisible(["inicio","cta"],TODAS); toggleNav(false); }
function mostrarLogin()             { setVisible(["login"],TODAS); }
function mostrarRegistro()          { setVisible(["registro"],TODAS); }
function mostrarVerify2FA()         { setVisible(["verify2fa"],TODAS); }
function mostrarDashboardNegocio()  { setVisible(["dashboard-negocio"],TODAS); toggleNav(true); }
function mostrarDashboardCliente()  { setVisible(["dashboard-cliente"],TODAS); toggleNav(true); }
function mostrarMiPerfil()          { setVisible(["mi-perfil"],TODAS); }
function mostrarRegistrarNegocio()  { setVisible(["registrar-negocio"],TODAS); }

function toggleNav(loggedIn) {
  document.getElementById("nav-public-btns").style.display    = loggedIn?"none":"flex";
  document.getElementById("nav-dashboard-btns").style.display = loggedIn?"flex":"none";
  const f=document.getElementById("footerMain"); if(f) f.style.display=loggedIn?"none":"block";
}

// ═══════════════════════════════════════
//  UTILIDADES
// ═══════════════════════════════════════
function mostrarMsg(id,texto,esError=true) {
  const el=document.getElementById(id); if(!el) return;
  el.textContent=texto; el.className="msg "+(esError?"error":"success"); el.style.display="block";
  if(!esError) setTimeout(()=>el.style.display="none",3500);
}
function getToken()   { return localStorage.getItem("access_token"); }
function getUsuario() { return JSON.parse(localStorage.getItem("usuario")||"null"); }
function formatPrecio(v) { return new Intl.NumberFormat('es-CO',{style:'currency',currency:'COP',maximumFractionDigits:0}).format(v); }
function abrirModal(id)  { document.getElementById(id).classList.add("open"); }
function cerrarModal(id) { document.getElementById(id).classList.remove("open"); }
function emptyState(msg) { return `<tr><td colspan="10"><div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-text">${msg}</div></div></td></tr>`; }
function errorDetail(data) { if(!data.detail) return "Error desconocido."; return typeof data.detail==='string'?data.detail:JSON.stringify(data.detail); }

document.querySelectorAll('.modal-overlay').forEach(o => {
  o.addEventListener('click', e => { if(e.target===o) o.classList.remove('open'); });
});

// ═══════════════════════════════════════
//  REGISTRO
// ═══════════════════════════════════════
document.getElementById("registroForm")?.addEventListener("submit", async(e) => {
  e.preventDefault();
  const btn=e.target.querySelector('button[type="submit"]');
  btn.innerHTML='<span class="loader"></span>Registrando...'; btn.disabled=true;
  const rol=document.querySelector('input[name="rolRegistro"]:checked')?.value||"cliente";
  const payload={nombre:document.getElementById("nombre").value.trim(),apellido:document.getElementById("apellido").value.trim(),correo:document.getElementById("correo").value.trim(),telefono:document.getElementById("telefono").value.trim(),password:document.getElementById("password").value,rol};
  try {
    const res=await fetch(`${API_BASE}/auth/register`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const data=await res.json();
    if(res.status===201) { mostrarMsg("registroMsg"," Cuenta creada. Redirigiendo...",false); setTimeout(mostrarLogin,1800); }
    else mostrarMsg("registroMsg",errorDetail(data));
  } catch { mostrarMsg("registroMsg","No se pudo conectar."); }
  finally { btn.innerHTML='Registrarse'; btn.disabled=false; }
});

// ═══════════════════════════════════════
//  LOGIN
// ═══════════════════════════════════════
document.getElementById("loginForm")?.addEventListener("submit", async(e) => {
  e.preventDefault();
  const btn=document.getElementById("loginBtn");
  btn.innerHTML='<span class="loader"></span>Entrando...'; btn.disabled=true;
  const payload={correo:document.getElementById("loginCorreo").value.trim(),password:document.getElementById("loginPassword").value};
  try {
    const res=await fetch(`${API_BASE}/auth/login`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const data=await res.json();
    if(res.ok&&data.requieres_2fa) { sessionStorage.setItem("correo_2fa",data.correo); mostrarVerify2FA(); mostrarMsg("verify2faMsg","📧 Código enviado a tu correo.",false); }
    else mostrarMsg("loginMsg",data.detail||"Credenciales inválidas.");
  } catch { mostrarMsg("loginMsg","No se pudo conectar."); }
  finally { btn.innerHTML='Entrar'; btn.disabled=false; }
});

// ═══════════════════════════════════════
//  2FA
// ═══════════════════════════════════════
document.getElementById("verify2faForm")?.addEventListener("submit", async(e) => {
  e.preventDefault();
  const payload={correo:sessionStorage.getItem("correo_2fa"),codigo:document.getElementById("codigo2fa").value.trim()};
  try {
    const res=await fetch(`${API_BASE}/auth/verify-2fa`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const data=await res.json();
    if(res.ok) {
      localStorage.setItem("access_token",data.access_token);
      localStorage.setItem("usuario",JSON.stringify(data.usuario));
      sessionStorage.removeItem("correo_2fa");
      if(data.usuario.rol==="negocio"||data.usuario.rol==="admin") { mostrarDashboardNegocio(); cargarDatosDashboard(data.usuario); }
      else { mostrarDashboardCliente(); cargarDatosCliente(data.usuario); }
    } else mostrarMsg("verify2faMsg",data.detail||"Código inválido.");
  } catch { mostrarMsg("verify2faMsg","No se pudo conectar."); }
});

// ═══════════════════════════════════════
//  DASHBOARD NEGOCIO
// ═══════════════════════════════════════
async function cargarDatosDashboard(usuario) {
  const el=document.getElementById("dashNombreUsuario"); if(el) el.textContent=`${usuario.nombre} ${usuario.apellido}`;
  document.getElementById("navUserName").textContent=usuario.nombre;
  const token=getToken(); if(!token) return;
  try {
    const res=await fetch(`${API_BASE}/negocios/`,{headers:{"Authorization":`Bearer ${token}`}});
    const data=await res.json();
    const miNegocio=Array.isArray(data)?data.find(n=>n.id_usuario_propietario===usuario.id):null;
    const span=document.getElementById("dashNombreNegocio");
    if(miNegocio) { negocioActual=miNegocio; if(span) span.textContent=miNegocio.nombre_negocio; cargarEstadisticas(miNegocio.id_negocio,token); }
    else { if(span) span.textContent="Sin negocio — ve a 'Mi Negocio' para crear uno"; }
  } catch {}
}
async function cargarEstadisticas(idNegocio,token) {
  document.getElementById("dashStats").style.display="grid";
  try {
    const [sR,eR,pR,cR]=await Promise.allSettled([
      fetch(`${API_BASE}/servicios/?id_negocio=${idNegocio}`,{headers:{"Authorization":`Bearer ${token}`}}),
      fetch(`${API_BASE}/empleados/?id_negocio=${idNegocio}`,{headers:{"Authorization":`Bearer ${token}`}}),
      fetch(`${API_BASE}/productos/?id_negocio=${idNegocio}`,{headers:{"Authorization":`Bearer ${token}`}}),
      fetch(`${API_BASE}/citas/negocio/${idNegocio}`,{headers:{"Authorization":`Bearer ${token}`}}),
    ]);
    const p=async r=>{if(r.status==='fulfilled'&&r.value.ok){const d=await r.value.json();return Array.isArray(d)?d.length:0;}return 0;};
    document.getElementById("statServicios").textContent=await p(sR);
    document.getElementById("statEmpleados").textContent=await p(eR);
    document.getElementById("statProductos").textContent=await p(pR);
    document.getElementById("statCitas").textContent=await p(cR);
  } catch {}
}

// ═══════════════════════════════════════
//  DASHBOARD CLIENTE
// ═══════════════════════════════════════
async function cargarDatosCliente(usuario) {
  const el=document.getElementById("clienteNombreUsuario"); if(el) el.textContent=`${usuario.nombre} ${usuario.apellido}`;
  document.getElementById("navUserName").textContent=usuario.nombre;
}

function cerrarSesion() {
  localStorage.removeItem("access_token"); localStorage.removeItem("usuario"); negocioActual=null; mostrarInicio();
}

// ═══════════════════════════════════════
//  PERFIL — FIX: con edición
// ═══════════════════════════════════════
async function irMiPerfil() {
  const token=getToken(); if(!token){mostrarLogin();return;}
  try {
    const res=await fetch(`${API_BASE}/auth/me`,{headers:{"Authorization":`Bearer ${token}`}});
    const data=await res.json();
    if(res.ok) {
      document.getElementById("perfilNombre").textContent=data.nombre;
      document.getElementById("perfilApellido").textContent=data.apellido;
      document.getElementById("perfilCorreo").textContent=data.correo;
      document.getElementById("perfilTelefono").textContent=data.telefono||"—";
      document.getElementById("perfilRol").textContent=ROLES[data.rol]||data.rol;
      document.getElementById("perfilEstado").textContent=data.estado||"activo";
    }
  } catch {}
  document.getElementById("perfilEditarForm").style.display="none";
  mostrarMiPerfil();
}

document.getElementById("editarPerfilForm")?.addEventListener("submit", async(e) => {
  e.preventDefault();
  const token=getToken(); if(!token) return;
  const payload={};
  const nombre=document.getElementById("editNombre").value.trim();
  const apellido=document.getElementById("editApellido").value.trim();
  const telefono=document.getElementById("editTelefono").value.trim();
  const password=document.getElementById("editPassword").value;
  if(nombre) payload.nombre=nombre;
  if(apellido) payload.apellido=apellido;
  if(telefono) payload.telefono=telefono;
  if(password) payload.password=password;
  try {
    const res=await fetch(`${API_BASE}/auth/me`,{method:"PUT",headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`},body:JSON.stringify(payload)});
    const data=await res.json();
    if(res.ok) {
      mostrarMsg("editarPerfilMsg"," Perfil actualizado.",false);
      // Actualizar vista
      if(nombre) document.getElementById("perfilNombre").textContent=nombre;
      if(apellido) document.getElementById("perfilApellido").textContent=apellido;
      if(telefono) document.getElementById("perfilTelefono").textContent=telefono;
      // Actualizar localStorage
      const u=getUsuario(); if(u){if(nombre)u.nombre=nombre;if(apellido)u.apellido=apellido;localStorage.setItem("usuario",JSON.stringify(u));}
      setTimeout(()=>document.getElementById("perfilEditarForm").style.display="none",2000);
    } else mostrarMsg("editarPerfilMsg",errorDetail(data));
  } catch { mostrarMsg("editarPerfilMsg","Error de conexión."); }
});

// ═══════════════════════════════════════
//  NEGOCIO
// ═══════════════════════════════════════
function irRegistrarNegocio() {
  if(negocioActual) {
    document.getElementById("negNombre").value=negocioActual.nombre_negocio||"";
    document.getElementById("negDescripcion").value=negocioActual.descripcion||"";
    document.getElementById("negDireccion").value=negocioActual.direccion||"";
    document.getElementById("negCiudad").value=negocioActual.ciudad||"";
    document.getElementById("negTelefono").value=negocioActual.telefono||"";
    document.getElementById("negCorreo").value=negocioActual.email_negocio||"";
  }
  mostrarRegistrarNegocio();
}
document.getElementById("negocioForm")?.addEventListener("submit", async(e) => {
  e.preventDefault();
  const token=getToken(); if(!token){mostrarLogin();return;}
  const btn=e.target.querySelector('button[type="submit"]');
  btn.innerHTML='<span class="loader"></span>Guardando...'; btn.disabled=true;
  const payload={nombre:document.getElementById("negNombre").value.trim(),descripcion:document.getElementById("negDescripcion").value.trim()||null,direccion:document.getElementById("negDireccion").value.trim()||null,ciudad:document.getElementById("negCiudad").value.trim()||null,telefono:document.getElementById("negTelefono").value.trim()||null,email_negocio:document.getElementById("negCorreo").value.trim()||null};
  try {
    let res;
    if(negocioActual) res=await fetch(`${API_BASE}/negocios/${negocioActual.id_negocio}`,{method:"PUT",headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`},body:JSON.stringify(payload)});
    else res=await fetch(`${API_BASE}/negocios/`,{method:"POST",headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`},body:JSON.stringify(payload)});
    const data=await res.json();
    if(res.ok||res.status===201) {
      mostrarMsg("negocioMsg"," Negocio guardado.",false);
      negocioActual=data.negocio||data;
      document.getElementById("dashNombreNegocio").textContent=negocioActual.nombre_negocio||negocioActual.nombre||payload.nombre;
    } else mostrarMsg("negocioMsg",errorDetail(data));
  } catch { mostrarMsg("negocioMsg","Error de conexión."); }
  finally { btn.innerHTML='Guardar Negocio'; btn.disabled=false; }
});

// ═══════════════════════════════════════
//  SERVICIOS
// ═══════════════════════════════════════
async function irServicios() {
  if(!negocioActual){alert("Primero registra tu negocio.");irRegistrarNegocio();return;}
  setVisible(["servicios"],TODAS); toggleNav(true); await cargarServicios();
}
async function cargarServicios() {
  const token=getToken(); const tbody=document.getElementById("bodyServicios");
  tbody.innerHTML=`<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--gray);"><span class="loader"></span></td></tr>`;
  try {
    const res=await fetch(`${API_BASE}/servicios/?id_negocio=${negocioActual.id_negocio}`,{headers:{"Authorization":`Bearer ${token}`}});
    const data=await res.json();
    if(!Array.isArray(data)||data.length===0){tbody.innerHTML=emptyState("No hay servicios");return;}
    tbody.innerHTML=data.map(s=>`<tr><td><strong>${s.nombre}</strong><br><span style="font-size:0.7rem;color:var(--gray);">${s.descripcion||''}</span></td><td>${s.duracion_minutos} min</td><td>${formatPrecio(s.precio)}</td><td><span class="badge badge-${s.estado}">${s.estado}</span></td><td><button class="btn-table" onclick="editarServicio(${s.id_servicio})">Editar</button><button class="btn-table btn-table-danger" onclick="confirmarEliminar('servicio',${s.id_servicio})">Eliminar</button></td></tr>`).join("");
  } catch { tbody.innerHTML=emptyState("Error al cargar"); }
}
function abrirModalServicio(id=null) {
  document.getElementById("modalServicioTitle").textContent=id?"Editar Servicio":"Nuevo Servicio";
  document.getElementById("servicioId").value=id||"";
  if(!id){["svcNombre","svcDescripcion","svcDuracion","svcPrecio"].forEach(f=>document.getElementById(f).value="");document.getElementById("svcEstado").value="activo";}
  document.getElementById("modalServicioMsg").style.display="none"; abrirModal("modalServicio");
}
async function editarServicio(id) {
  const token=getToken();
  try{const res=await fetch(`${API_BASE}/servicios/${id}`,{headers:{"Authorization":`Bearer ${token}`}});const s=await res.json();abrirModalServicio(id);document.getElementById("svcNombre").value=s.nombre;document.getElementById("svcDescripcion").value=s.descripcion||"";document.getElementById("svcDuracion").value=s.duracion_minutos;document.getElementById("svcPrecio").value=s.precio;document.getElementById("svcEstado").value=s.estado;}catch{}
}
async function guardarServicio() {
  const token=getToken();const id=document.getElementById("servicioId").value;
  const payload={nombre:document.getElementById("svcNombre").value.trim(),descripcion:document.getElementById("svcDescripcion").value.trim()||null,duracion_minutos:parseInt(document.getElementById("svcDuracion").value),precio:parseFloat(document.getElementById("svcPrecio").value),estado:document.getElementById("svcEstado").value,id_negocio:negocioActual.id_negocio};
  if(!payload.nombre||!payload.duracion_minutos||!payload.precio){mostrarMsg("modalServicioMsg","Completa los campos obligatorios.");return;}
  try{const url=id?`${API_BASE}/servicios/${id}`:`${API_BASE}/servicios/`;const res=await fetch(url,{method:id?"PUT":"POST",headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`},body:JSON.stringify(payload)});const data=await res.json();if(res.ok||res.status===201){cerrarModal("modalServicio");await cargarServicios();mostrarMsg("serviciosMsg","✅ Servicio guardado.",false);}else mostrarMsg("modalServicioMsg",errorDetail(data));}catch{mostrarMsg("modalServicioMsg","Error de conexión.");}
}

// ═══════════════════════════════════════
//  EMPLEADOS
// ═══════════════════════════════════════
async function irEmpleados() {
  if(!negocioActual){alert("Primero registra tu negocio.");irRegistrarNegocio();return;}
  setVisible(["empleados"],TODAS); toggleNav(true); await cargarEmpleados();
}
async function cargarEmpleados() {
  const token=getToken();const tbody=document.getElementById("bodyEmpleados");
  tbody.innerHTML=`<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--gray);"><span class="loader"></span></td></tr>`;
  try{const res=await fetch(`${API_BASE}/empleados/?id_negocio=${negocioActual.id_negocio}`,{headers:{"Authorization":`Bearer ${token}`}});const data=await res.json();if(!Array.isArray(data)||data.length===0){tbody.innerHTML=emptyState("No hay empleados");return;}tbody.innerHTML=data.map(emp=>`<tr><td><strong>${emp.nombre} ${emp.apellido}</strong></td><td>${emp.especialidad||'—'}</td><td>${emp.telefono||'—'}</td><td><span class="badge badge-${emp.estado}">${emp.estado}</span></td><td><button class="btn-table" onclick="editarEmpleado(${emp.id_empleado})">Editar</button><button class="btn-table btn-table-danger" onclick="confirmarEliminar('empleado',${emp.id_empleado})">Eliminar</button></td></tr>`).join("");}catch{tbody.innerHTML=emptyState("Error al cargar");}
}
function abrirModalEmpleado(id=null) {
  document.getElementById("modalEmpleadoTitle").textContent=id?"Editar Empleado":"Nuevo Empleado";
  document.getElementById("empleadoId").value=id||"";
  if(!id){["empNombre","empApellido","empEspecialidad","empTelefono","empEmail"].forEach(f=>document.getElementById(f).value="");document.getElementById("empEstado").value="activo";}
  document.getElementById("modalEmpleadoMsg").style.display="none"; abrirModal("modalEmpleado");
}
async function editarEmpleado(id) {
  const token=getToken();try{const res=await fetch(`${API_BASE}/empleados/${id}`,{headers:{"Authorization":`Bearer ${token}`}});const emp=await res.json();abrirModalEmpleado(id);document.getElementById("empNombre").value=emp.nombre;document.getElementById("empApellido").value=emp.apellido;document.getElementById("empEspecialidad").value=emp.especialidad||"";document.getElementById("empTelefono").value=emp.telefono||"";document.getElementById("empEmail").value=emp.email||"";document.getElementById("empEstado").value=emp.estado;}catch{}
}
async function guardarEmpleado() {
  const token=getToken();const id=document.getElementById("empleadoId").value;
  const payload={nombre:document.getElementById("empNombre").value.trim(),apellido:document.getElementById("empApellido").value.trim(),especialidad:document.getElementById("empEspecialidad").value.trim()||null,telefono:document.getElementById("empTelefono").value.trim()||null,email:document.getElementById("empEmail").value.trim()||null,estado:document.getElementById("empEstado").value,id_negocio:negocioActual.id_negocio};
  if(!payload.nombre||!payload.apellido){mostrarMsg("modalEmpleadoMsg","Nombre y apellido son obligatorios.");return;}
  try{const url=id?`${API_BASE}/empleados/${id}`:`${API_BASE}/empleados/`;const res=await fetch(url,{method:id?"PUT":"POST",headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`},body:JSON.stringify(payload)});const data=await res.json();if(res.ok||res.status===201){cerrarModal("modalEmpleado");await cargarEmpleados();mostrarMsg("empleadosMsg"," Empleado guardado.",false);}else mostrarMsg("modalEmpleadoMsg",errorDetail(data));}catch{mostrarMsg("modalEmpleadoMsg","Error de conexión.");}
}

// ═══════════════════════════════════════
//  PRODUCTOS
// ═══════════════════════════════════════
async function irProductos() {
  if(!negocioActual){alert("Primero registra tu negocio.");irRegistrarNegocio();return;}
  setVisible(["productos"],TODAS); toggleNav(true); await cargarProductos();
}
async function cargarProductos() {
  const token=getToken();const tbody=document.getElementById("bodyProductos");
  tbody.innerHTML=`<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--gray);"><span class="loader"></span></td></tr>`;
  try{const res=await fetch(`${API_BASE}/productos/?id_negocio=${negocioActual.id_negocio}`,{headers:{"Authorization":`Bearer ${token}`}});const data=await res.json();if(!Array.isArray(data)||data.length===0){tbody.innerHTML=emptyState("No hay productos");return;}tbody.innerHTML=data.map(p=>`<tr><td><strong>${p.nombre}</strong></td><td>${formatPrecio(p.precio)}</td><td>${p.stock}</td><td><span class="badge badge-${p.estado}">${p.estado}</span></td><td><button class="btn-table" onclick="editarProducto(${p.id_producto})">Editar</button><button class="btn-table btn-table-danger" onclick="confirmarEliminar('producto',${p.id_producto})">Eliminar</button></td></tr>`).join("");}catch{tbody.innerHTML=emptyState("Error al cargar");}
}
function abrirModalProducto(id=null) {
  document.getElementById("modalProductoTitle").textContent=id?"Editar Producto":"Nuevo Producto";
  document.getElementById("productoId").value=id||"";
  if(!id){["prodNombre","prodDescripcion","prodPrecio","prodStock"].forEach(f=>document.getElementById(f).value="");document.getElementById("prodEstado").value="activo";}
  document.getElementById("modalProductoMsg").style.display="none"; abrirModal("modalProducto");
}
async function editarProducto(id) {
  const token=getToken();try{const res=await fetch(`${API_BASE}/productos/${id}`,{headers:{"Authorization":`Bearer ${token}`}});const p=await res.json();abrirModalProducto(id);document.getElementById("prodNombre").value=p.nombre;document.getElementById("prodDescripcion").value=p.descripcion||"";document.getElementById("prodPrecio").value=p.precio;document.getElementById("prodStock").value=p.stock;document.getElementById("prodEstado").value=p.estado;}catch{}
}
async function guardarProducto() {
  const token=getToken();const id=document.getElementById("productoId").value;
  const payload={nombre:document.getElementById("prodNombre").value.trim(),descripcion:document.getElementById("prodDescripcion").value.trim()||null,precio:parseFloat(document.getElementById("prodPrecio").value),stock:parseInt(document.getElementById("prodStock").value),estado:document.getElementById("prodEstado").value,id_negocio:negocioActual.id_negocio};
  if(!payload.nombre||isNaN(payload.precio)||isNaN(payload.stock)){mostrarMsg("modalProductoMsg","Completa los campos.");return;}
  try{const url=id?`${API_BASE}/productos/${id}`:`${API_BASE}/productos/`;const res=await fetch(url,{method:id?"PUT":"POST",headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`},body:JSON.stringify(payload)});const data=await res.json();if(res.ok||res.status===201){cerrarModal("modalProducto");await cargarProductos();mostrarMsg("productosMsg","✅ Producto guardado.",false);}else mostrarMsg("modalProductoMsg",errorDetail(data));}catch{mostrarMsg("modalProductoMsg","Error de conexión.");}
}

// ═══════════════════════════════════════
//  CITAS PROPIETARIO
// ═══════════════════════════════════════
async function irCitas() {
  if(!negocioActual){alert("Primero registra tu negocio.");irRegistrarNegocio();return;}
  setVisible(["citas"],TODAS); toggleNav(true); await cargarCitas();
}
async function cargarCitas() {
  const token=getToken(); const tbody=document.getElementById("bodyCitas");
  tbody.innerHTML=`<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--gray);"><span class="loader"></span></td></tr>`;
  if(!negocioActual){tbody.innerHTML=emptyState("Registra tu negocio primero");return;}
  try{
    const res=await fetch(`${API_BASE}/citas/negocio/${negocioActual.id_negocio}`,{headers:{"Authorization":`Bearer ${token}`}});
    const data=await res.json();
    if(!Array.isArray(data)||data.length===0){tbody.innerHTML=emptyState("No hay citas registradas");return;}
    tbody.innerHTML=data.map(c=>{
      const inicio=c.fecha_hora_inicio?new Date(c.fecha_hora_inicio).toLocaleString('es-CO'):'-';
      const fin=c.fecha_hora_fin?new Date(c.fecha_hora_fin).toLocaleTimeString('es-CO',{hour:'2-digit',minute:'2-digit'}):'-';
      return `<tr><td>${inicio}</td><td>${fin}</td><td><span class="badge badge-${c.estado}">${c.estado}</span></td><td style="font-size:0.75rem;color:var(--gray);">${c.observaciones||'—'}</td><td><button class="btn-table btn-table-danger" onclick="confirmarEliminar('cita',${c.id_cita})">Cancelar</button></td></tr>`;
    }).join("");
  }catch(e){console.error(e);tbody.innerHTML=emptyState("Error al cargar citas");}
}
async function abrirModalCita() {
  const token=getToken();

  // Cargar empleados
  const selEmp=document.getElementById("citaEmpleado");
  selEmp.innerHTML='<option value="">Cargando empleados...</option>';
  try{
    const res=await fetch(`${API_BASE}/empleados/?id_negocio=${negocioActual.id_negocio}`,{headers:{"Authorization":`Bearer ${token}`}});
    const data=await res.json();
    selEmp.innerHTML='<option value="">Seleccionar empleado...</option>';
    if(Array.isArray(data)&&data.length>0) data.forEach(emp=>{selEmp.innerHTML+=`<option value="${emp.id_empleado}">${emp.nombre} ${emp.apellido}</option>`;});
    else selEmp.innerHTML='<option value="">No hay empleados</option>';
  }catch{selEmp.innerHTML='<option value="">Error al cargar</option>';}

  // Cargar clientes
  const selCli=document.getElementById("citaCliente");
  if(selCli){
    selCli.innerHTML='<option value="">Cargando clientes...</option>';
    try{
      const res=await fetch(`${API_BASE}/auth/usuarios`,{headers:{"Authorization":`Bearer ${token}`}});
      const data=await res.json();
      selCli.innerHTML='<option value="">Seleccionar cliente...</option>';
      if(Array.isArray(data)&&data.length>0){
        data.filter(u=>u.rol==="cliente").forEach(u=>{selCli.innerHTML+=`<option value="${u.id_usuario}">${u.nombre} ${u.apellido} (${u.correo})</option>`;});
      }
    }catch{
      // Si no hay endpoint de usuarios, dejar campo manual
      selCli.innerHTML='<option value="">No disponible</option>';
    }
  }

  ["citaFecha","citaHoraInicio","citaHoraFin","citaObservaciones"].forEach(f=>document.getElementById(f).value="");
  document.getElementById("modalCitaMsg").style.display="none";
  abrirModal("modalCita");
}

async function guardarCita() {
  const token=getToken();

  const idEmpleado=parseInt(document.getElementById("citaEmpleado").value);
  const fecha=document.getElementById("citaFecha").value;
  const horaRaw1=document.getElementById("citaHoraInicio").value;
  const horaRaw2=document.getElementById("citaHoraFin").value;
  const horaInicio=horaRaw1.length===5?horaRaw1+":00":horaRaw1;
  const horaFin=horaRaw2.length===5?horaRaw2+":00":horaRaw2;

  // id_cliente: desde select o campo manual
  const selCli=document.getElementById("citaCliente");
  const inputCli=document.getElementById("citaClienteId");
  let idCliente=null;
  if(selCli&&selCli.value) idCliente=parseInt(selCli.value);
  else if(inputCli&&inputCli.value) idCliente=parseInt(inputCli.value);

  if(!fecha||!horaInicio||!horaFin||isNaN(idEmpleado)||!idCliente){
    mostrarMsg("modalCitaMsg","Completa todos los campos, incluyendo el cliente.");return;
  }

  const payload={
    fecha, hora_inicio:horaInicio, hora_fin:horaFin,
    id_empleado:idEmpleado, id_negocio:negocioActual.id_negocio,
    id_cliente:idCliente,
    observaciones:document.getElementById("citaObservaciones").value.trim()||null
  };

  console.log("Payload cita negocio:", JSON.stringify(payload));

  try{
    const res=await fetch(`${API_BASE}/citas/`,{method:"POST",headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`},body:JSON.stringify(payload)});
    const data=await res.json();
    console.log("Resp:", res.status, data);
    if(res.ok||res.status===201){cerrarModal("modalCita");await cargarCitas();mostrarMsg("citasMsg","Cita agendada correctamente.",false);}
    else mostrarMsg("modalCitaMsg",errorDetail(data));
  }catch(e){console.error(e);mostrarMsg("modalCitaMsg","Error de conexion.");}
}

// ═══════════════════════════════════════
//  CITAS CLIENTE — FIX: cliente puede agendar
// ═══════════════════════════════════════
async function irMisCitas() {
  setVisible(["mis-citas"],TODAS); toggleNav(true); await cargarMisCitas();
}
async function cargarMisCitas() {
  const token=getToken(); const usuario=getUsuario(); const tbody=document.getElementById("bodyMisCitas");
  tbody.innerHTML=`<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--gray);"><span class="loader"></span></td></tr>`;
  if(!usuario){tbody.innerHTML=emptyState("Inicia sesion primero");return;}
  try{
    const res=await fetch(`${API_BASE}/citas/cliente/${usuario.id}`,{headers:{"Authorization":`Bearer ${token}`}});
    const data=await res.json();
    if(!Array.isArray(data)||data.length===0){tbody.innerHTML=emptyState("No tienes citas");return;}
    tbody.innerHTML=data.map(c=>{
      const inicio=c.fecha_hora_inicio?new Date(c.fecha_hora_inicio).toLocaleString('es-CO'):'-';
      const fin=c.fecha_hora_fin?new Date(c.fecha_hora_fin).toLocaleTimeString('es-CO',{hour:'2-digit',minute:'2-digit'}):'-';
      return `<tr><td>${inicio}</td><td>${fin}</td><td>-</td><td><span class="badge badge-${c.estado}">${c.estado}</span></td><td><button class="btn-table btn-table-danger" onclick="confirmarEliminarCitaCliente(${c.id_cita})">Cancelar</button></td></tr>`;
    }).join("");
  }catch(e){console.error(e);tbody.innerHTML=emptyState("Error al cargar citas");}
}

async function abrirModalCitaCliente(negocioPreseleccionado=null) {
  const token=getToken();
  // Cargar negocios en select
  const selNegocio=document.getElementById("citaClienteNegocio");
  selNegocio.innerHTML='<option value="">Cargando negocios...</option>';
  try{
    const res=await fetch(`${API_BASE}/negocios/`,{headers:{"Authorization":`Bearer ${token}`}});
    const data=await res.json();
    todosLosNegocios=Array.isArray(data)?data:[];
    selNegocio.innerHTML='<option value="">Seleccionar negocio...</option>';
    if(todosLosNegocios.length===0) selNegocio.innerHTML='<option value="">No hay negocios registrados</option>';
    else todosLosNegocios.forEach(n=>{selNegocio.innerHTML+=`<option value="${n.id_negocio}">${n.nombre_negocio}</option>`;});
    if(negocioPreseleccionado) { selNegocio.value=negocioPreseleccionado; await cargarEmpleadosCliente(negocioPreseleccionado); }
  }catch(err){console.error("Error negocios:",err);selNegocio.innerHTML='<option value="">Error al cargar</option>';}
  document.getElementById("citaClienteEmpleado").innerHTML='<option value="">Seleccionar empleado...</option>';
  ["citaClienteFecha","citaClienteHoraInicio","citaClienteHoraFin","citaClienteObservaciones"].forEach(f=>document.getElementById(f).value="");
  document.getElementById("modalCitaClienteMsg").style.display="none";
  abrirModal("modalCitaCliente");
}

async function cargarEmpleadosCliente(idNegocio) {
  if(!idNegocio) return;
  const token=getToken();
  const sel=document.getElementById("citaClienteEmpleado");
  sel.innerHTML='<option value="">Cargando empleados...</option>';
  try{
    const id=parseInt(idNegocio);
    console.log("Cargando empleados para negocio:", id);
    const res=await fetch(`${API_BASE}/empleados/?id_negocio=${id}`,{headers:{"Authorization":`Bearer ${token}`}});
    const data=await res.json();
    console.log("Empleados recibidos:", data);
    sel.innerHTML='<option value="">Seleccionar empleado...</option>';
    if(Array.isArray(data)&&data.length>0){
      data.forEach(emp=>{sel.innerHTML+=`<option value="${emp.id_empleado}">${emp.nombre} ${emp.apellido}</option>`;});
    } else {
      sel.innerHTML='<option value="">Sin empleados en este negocio</option>';
    }
  }catch(e){
    console.error("Error empleados:", e);
    sel.innerHTML='<option value="">Error al cargar</option>';
  }
}

async function guardarCitaCliente() {
  const token=getToken();
  const usuario=getUsuario();
  if(!token||!usuario){mostrarMsg("modalCitaClienteMsg","Sesión expirada.");return;}
  const idNegocio=parseInt(document.getElementById("citaClienteNegocio").value);
  const idEmpleado=parseInt(document.getElementById("citaClienteEmpleado").value);
  const fecha=document.getElementById("citaClienteFecha").value;
  const horaRaw1=document.getElementById("citaClienteHoraInicio").value;
  const horaRaw2=document.getElementById("citaClienteHoraFin").value;
  const horaInicio=horaRaw1.length===5?horaRaw1+":00":horaRaw1;
  const horaFin=horaRaw2.length===5?horaRaw2+":00":horaRaw2;
  if(!fecha||!horaInicio||!horaFin||isNaN(idEmpleado)||isNaN(idNegocio)){mostrarMsg("modalCitaClienteMsg","Completa todos los campos.");return;}
  const payload={fecha,hora_inicio:horaInicio,hora_fin:horaFin,id_empleado:idEmpleado,id_negocio:idNegocio,id_cliente:usuario.id,observaciones:document.getElementById("citaClienteObservaciones").value.trim()||null};
  console.log("Payload cita:", JSON.stringify(payload));
  try{
    const res=await fetch(`${API_BASE}/citas/`,{method:"POST",headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`},body:JSON.stringify(payload)});
    const data=await res.json();
    console.log("Resp cita:",res.status,data);
    if(res.ok||res.status===201){cerrarModal("modalCitaCliente");await cargarMisCitas();mostrarMsg("misCitasMsg","Cita agendada exitosamente.",false);}
    else mostrarMsg("modalCitaClienteMsg",errorDetail(data));
  }catch(err){console.error("Error:",err);mostrarMsg("modalCitaClienteMsg","Error de conexion. Revisa F12.");}
}

function confirmarEliminarCitaCliente(id) {
  document.getElementById("modalConfirmarTexto").textContent="¿Cancelar esta cita? No se puede deshacer.";
  document.getElementById("btnConfirmarEliminar").onclick=()=>eliminarCitaCliente(id);
  abrirModal("modalConfirmar");
}
async function eliminarCitaCliente(id) {
  const token=getToken();
  try{const res=await fetch(`${API_BASE}/citas/${id}`,{method:"DELETE",headers:{"Authorization":`Bearer ${token}`}});cerrarModal("modalConfirmar");if(res.ok||res.status===204)await cargarMisCitas();}catch{}
}

// ═══════════════════════════════════════
//  VER NEGOCIOS — FIX: ahora carga correctamente
// ═══════════════════════════════════════
async function irVerNegocios() {
  setVisible(["ver-negocios"],TODAS); toggleNav(true);
  const contenedor=document.getElementById("listaNegocios");
  contenedor.innerHTML=`<div style="text-align:center;padding:40px;color:var(--gray);"><span class="loader"></span> Cargando...</div>`;
  try{
    const res=await fetch(`${API_BASE}/negocios/`,{headers:{"Authorization":`Bearer ${getToken()}`}});
    const data=await res.json();
    if(!Array.isArray(data)||data.length===0){contenedor.innerHTML=`<div class="empty-state"><div class="empty-state-icon"></div><div class="empty-state-text">No hay negocios registrados</div></div>`;return;}
    contenedor.innerHTML=data.map(n=>`<div class="negocio-card"><div class="negocio-card-nombre">${n.nombre_negocio}</div><div class="negocio-card-info">${n.descripcion?`<p>${n.descripcion}</p>`:''}${n.direccion?`<p> ${n.direccion}${n.ciudad?', '+n.ciudad:''}</p>`:''}${n.telefono?`<p> ${n.telefono}</p>`:''}${n.email_negocio?`<p> ${n.email_negocio}</p>`:''}</div></div>`).join("");
  }catch{contenedor.innerHTML=`<p style="color:#e74c3c;">Error de conexión.</p>`;}
}

// FIX: Ver negocios para CLIENTE con botón "Agendar Cita"
async function irVerNegociosCliente() {
  setVisible(["ver-negocios-cliente"],TODAS); toggleNav(true);
  const contenedor=document.getElementById("listaNegociosCliente");
  contenedor.innerHTML=`<div style="text-align:center;padding:40px;color:var(--gray);"><span class="loader"></span> Cargando...</div>`;
  try{
    const res=await fetch(`${API_BASE}/negocios/`,{headers:{"Authorization":`Bearer ${getToken()}`}});
    const data=await res.json();
    if(!Array.isArray(data)||data.length===0){contenedor.innerHTML=`<div class="empty-state"><div class="empty-state-icon"></div><div class="empty-state-text">No hay negocios registrados</div></div>`;return;}
    todosLosNegocios=data;
    contenedor.innerHTML=data.map(n=>`
      <div class="negocio-card">
        <div class="negocio-card-nombre">${n.nombre_negocio}</div>
        <div class="negocio-card-info">
          ${n.descripcion?`<p>${n.descripcion}</p>`:''}
          ${n.direccion?`<p> ${n.direccion}${n.ciudad?', '+n.ciudad:''}</p>`:''}
          ${n.telefono?`<p> ${n.telefono}</p>`:''}
        </div>
        <div style="margin-top:16px;">
          <button class="btn-primary" style="font-size:0.65rem;padding:10px 20px;" onclick="abrirModalCitaCliente(${n.id_negocio})"> Agendar Cita</button>
        </div>
      </div>`).join("");
  }catch{contenedor.innerHTML=`<p style="color:#e74c3c;">Error de conexión.</p>`;}
}

// ═══════════════════════════════════════
//  ELIMINAR GENÉRICO
// ═══════════════════════════════════════
function confirmarEliminar(tipo,id) {
  const textos={servicio:"este servicio",empleado:"este empleado",producto:"este producto",cita:"esta cita"};
  document.getElementById("modalConfirmarTexto").textContent=`¿Eliminar ${textos[tipo]||'este elemento'}? No se puede deshacer.`;
  document.getElementById("btnConfirmarEliminar").onclick=()=>eliminar(tipo,id);
  abrirModal("modalConfirmar");
}
async function eliminar(tipo,id) {
  const token=getToken();
  const urls={servicio:`${API_BASE}/servicios/${id}`,empleado:`${API_BASE}/empleados/${id}`,producto:`${API_BASE}/productos/${id}`,cita:`${API_BASE}/citas/${id}`};
  const recargar={servicio:cargarServicios,empleado:cargarEmpleados,producto:cargarProductos,cita:cargarCitas};
  try{const res=await fetch(urls[tipo],{method:"DELETE",headers:{"Authorization":`Bearer ${token}`}});cerrarModal("modalConfirmar");if(res.ok||res.status===204)await recargar[tipo]();else{const d=await res.json();alert(errorDetail(d));}}catch{alert("Error de conexión.");}
}

// ═══════════════════════════════════════
//  AUTO-LOGIN
// ═══════════════════════════════════════
(function checkSession() {
  const token=getToken();const usuario=getUsuario();
  if(token&&usuario){
    if(usuario.rol==="negocio"||usuario.rol==="admin"){mostrarDashboardNegocio();cargarDatosDashboard(usuario);}
    else{mostrarDashboardCliente();cargarDatosCliente(usuario);}
  }
})();