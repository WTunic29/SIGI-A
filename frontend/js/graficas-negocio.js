(function () {
  const charts = {};
  const GOLD = "#c9a84c";

  function el(id) {
    return document.getElementById(id);
  }

  function dinero(n) {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0
    }).format(Number(n || 0));
  }

  function iniciales(nombre, apellido) {
    return `${String(nombre || "?").charAt(0)}${String(apellido || "").charAt(0)}`.toUpperCase();
  }

  function destruirChart(id) {
    if (charts[id]) {
      charts[id].destroy();
      charts[id] = null;
    }
  }

  function crearChart(id, type, labels, data, options = {}) {
    const canvas = el(id);
    if (!canvas || typeof Chart === "undefined") return;

    destruirChart(id);

    charts[id] = new Chart(canvas.getContext("2d"), {
      type,
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: type === "line"
            ? "rgba(201,168,76,.18)"
            : labels.map((_, i) => `rgba(201,168,76,${0.35 + i * 0.07})`),
          borderColor: GOLD,
          borderWidth: type === "line" ? 2 : 0,
          borderRadius: type === "bar" ? 6 : 0,
          fill: type === "line",
          tension: 0.4,
          pointBackgroundColor: GOLD,
          pointRadius: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: options.horizontal ? "y" : "x",
        plugins: {
          legend: { display: type === "doughnut" },
        },
        scales: type === "doughnut" ? {} : {
          x: {
            grid: { color: "rgba(201,168,76,.06)" },
            ticks: { color: "rgba(232,224,208,.45)" }
          },
          y: {
            beginAtZero: true,
            grid: { color: "rgba(201,168,76,.06)" },
            ticks: { color: "rgba(232,224,208,.45)" }
          }
        }
      }
    });
  }

  function normalizarFecha(fecha) {
    return String(fecha || "").slice(0, 10);
  }

  function promedioCalificaciones(calificaciones) {
    if (!calificaciones.length) return 0;
    return calificaciones.reduce((s, c) => s + Number(c.puntuacion || 0), 0) / calificaciones.length;
  }

  function contarPorCampo(lista, campoFn) {
    const conteo = {};
    lista.forEach(item => {
      const key = campoFn(item);
      if (!key) return;
      conteo[key] = (conteo[key] || 0) + 1;
    });
    return conteo;
  }

  function topEntradas(obj, limite = 6) {
    return Object.entries(obj).sort((a, b) => b[1] - a[1]).slice(0, limite);
  }

  async function obtenerDatosAnaliticas(idNegocio) {
    const [citas, servicios, calificaciones] = await Promise.all([
      apiFetch(`/citas/negocio/${idNegocio}`).catch(() => []),
      apiFetch(API_PATHS.servicios).catch(() => []),
      apiFetch(API_PATHS.calificaciones).catch(() => [])
    ]);

    const citasLista = Array.isArray(citas) ? citas : [];
    const serviciosLista = (Array.isArray(servicios) ? servicios : [])
      .filter(s => Number(s.id_negocio) === Number(idNegocio));

    const calificacionesLista = (Array.isArray(calificaciones) ? calificaciones : [])
      .filter(c => Number(c.id_negocio) === Number(idNegocio));

    return {
      citas: citasLista,
      servicios: serviciosLista,
      calificaciones: calificacionesLista
    };
  }

  async function cargarAnaliticasNegocio() {
    const section = el("anaNegocioSection");
    if (!section) return;

    const negocio = await obtenerMiNegocio(true).catch(() => null);
    const idNegocio = Number(negocio?.id_negocio);

    if (!idNegocio) {
      section.style.display = "none";
      return;
    }

    section.style.display = "block";

    const { citas, servicios, calificaciones } = await obtenerDatosAnaliticas(idNegocio);

    const hoy = new Date().toISOString().slice(0, 10);
    const citasHoy = citas.filter(c => normalizarFecha(c.fecha) === hoy).length;
    const promedio = promedioCalificaciones(calificaciones);

    if (el("anaMetCitas")) el("anaMetCitas").textContent = citasHoy;
    if (el("anaMetTotalCitas")) el("anaMetTotalCitas").textContent = citas.length;
    if (el("anaMetCalif")) el("anaMetCalif").textContent = promedio ? `${promedio.toFixed(1)} ★` : "—";
    if (el("anaMetServicios")) el("anaMetServicios").textContent = servicios.length;

    const serviciosUsados = topEntradas(
      contarPorCampo(citas, c => c.servicio_nombre || "Sin servicio"),
      6
    );

    crearChart(
      "chartServUsados",
      "bar",
      serviciosUsados.map(x => x[0]),
      serviciosUsados.map(x => x[1]),
      { horizontal: true }
    );

    const estados = topEntradas(
      contarPorCampo(citas, c => c.estado || "sin_estado"),
      10
    );

    crearChart(
      "chartEstadosCitas",
      "doughnut",
      estados.map(x => x[0]),
      estados.map(x => x[1])
    );

    const dias = {};
    for (let i = 13; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const key = d.toISOString().slice(0, 10);
      dias[key] = 0;
    }

    citas.forEach(c => {
      const key = normalizarFecha(c.fecha);
      if (key in dias) dias[key]++;
    });

    crearChart(
      "chartCitasDia",
      "line",
      Object.keys(dias).map(f => f.slice(5)),
      Object.values(dias)
    );

    const empleadosConteo = {};
    citas.forEach(c => {
      const id = c.id_empleado;
      const nombre = `${c.empleado_nombre || ""} ${c.empleado_apellido || ""}`.trim() || `Empleado #${id}`;
      if (!empleadosConteo[id]) {
        empleadosConteo[id] = {
          nombre,
          iniciales: iniciales(c.empleado_nombre, c.empleado_apellido),
          total: 0
        };
      }
      empleadosConteo[id].total++;
    });

    const topEmpleados = Object.values(empleadosConteo)
      .sort((a, b) => b.total - a.total)
      .slice(0, 6);

    const topEl = el("anaTopEmpleados");
    if (topEl) {
      topEl.innerHTML = topEmpleados.length
        ? topEmpleados.map(e => `
          <div class="ana-emprow">
            <div class="ana-empav">${escapeHtml(e.iniciales)}</div>
            <div>
              <div class="ana-empname">${escapeHtml(e.nombre)}</div>
              <div class="ana-empsub">${escapeHtml(e.total)} cita${e.total === 1 ? "" : "s"}</div>
            </div>
            <div class="ana-empavg">${escapeHtml(e.total)}</div>
          </div>
        `).join("")
        : `<div class="empty-state">Sin datos de empleados todavía.</div>`;
    }

    const dist = [0, 0, 0, 0, 0];
    calificaciones.forEach(c => {
      const p = Math.max(1, Math.min(5, Math.round(Number(c.puntuacion || 0))));
      dist[p - 1]++;
    });

    crearChart(
      "chartCalifDist",
      "doughnut",
      ["1★", "2★", "3★", "4★", "5★"],
      dist
    );
  }

  let analiticasCargando = false;
  let analiticasCargadas = false;

  async function cargarAnaliticasNegocioSeguro(force = false) {
    if (analiticasCargando) return;
    if (analiticasCargadas && !force) return;

    analiticasCargando = true;

    try {
      await cargarAnaliticasNegocio();
      analiticasCargadas = true;
    } finally {
      analiticasCargando = false;
    }
  }

  window.cargarAnaliticasNegocio = cargarAnaliticasNegocio;
  window.cargarAnaliticasNegocioSeguro = cargarAnaliticasNegocioSeguro;

  document.addEventListener("DOMContentLoaded", () => {
    const observer = new MutationObserver(() => {
      const dash = el("dashboard-negocio");
      const visible = dash && dash.style.display !== "none";

      if (visible) {
        setTimeout(() => {
          cargarAnaliticasNegocioSeguro(false).catch(() => {});
        }, 300);
      }
    });

    observer.observe(document.body, {
      subtree: false,
      attributes: true,
      attributeFilter: ["style"]
    });

    setTimeout(() => {
      const dash = el("dashboard-negocio");
      if (dash && dash.style.display !== "none") {
        cargarAnaliticasNegocioSeguro(false).catch(() => {});
      }
    }, 800);
  });
})();
