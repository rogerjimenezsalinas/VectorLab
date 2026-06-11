/* VectorLab · frontend (vanilla JS) */
"use strict";

const $ = (id) => document.getElementById(id);
const API = "";  // mismo origen

/* ═══════════════ sesión ═══════════════ */
function usuarioActual() {
  try { return JSON.parse(localStorage.getItem("vectorlab_user")); }
  catch { return null; }
}
function guardarUsuario(u) { localStorage.setItem("vectorlab_user", JSON.stringify(u)); }
function cerrarSesion() { localStorage.removeItem("vectorlab_user"); mostrarVista(); }

function mostrarVista() {
  const u = usuarioActual();
  $("vista-acceso").classList.toggle("hidden", !!u);
  $("vista-app").classList.toggle("hidden", !u);
  $("user-chip").classList.toggle("hidden", !u);
  if (u) $("user-name").textContent = `${u.nombres} ${u.apellidos} · ${u.carnet_universitario}`;
}

/* ═══════════════ utilidades HTTP ═══════════════ */
async function post(ruta, cuerpo) {
  const res = await fetch(API + ruta, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo),
  });
  const datos = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(datos.detail || "Error de servidor");
  return datos;
}
function setMsg(id, texto, tipo) {
  const el = $(id);
  el.textContent = texto || "";
  el.className = "msg" + (tipo ? " " + tipo : "");
}

/* ═══════════════ registro / login ═══════════════ */
$("tab-registro").addEventListener("click", () => {
  $("tab-registro").classList.add("activa"); $("tab-login").classList.remove("activa");
  $("panel-registro").classList.remove("hidden"); $("panel-login").classList.add("hidden");
});
$("tab-login").addEventListener("click", () => {
  $("tab-login").classList.add("activa"); $("tab-registro").classList.remove("activa");
  $("panel-login").classList.remove("hidden"); $("panel-registro").classList.add("hidden");
});

$("btn-registrar").addEventListener("click", async () => {
  const cuerpo = {
    apellidos: $("r-apellidos").value.trim(),
    nombres: $("r-nombres").value.trim(),
    celular: $("r-celular").value.trim(),
    carnet_universitario: $("r-carnet").value.trim(),
    correo: $("r-correo").value.trim(),
    materia: $("r-materia").value.trim(),
    universidad: $("r-universidad").value.trim(),
  };
  if (Object.values(cuerpo).some(v => !v)) {
    return setMsg("msg-registro", "Completa todos los campos de la ficha.", "error");
  }
  $("btn-registrar").disabled = true;
  try {
    const u = await post("/api/registro", cuerpo);
    guardarUsuario(u);
    setMsg("msg-registro", "Registro exitoso. ¡Bienvenido!", "ok");
    mostrarVista();
  } catch (e) {
    setMsg("msg-registro", e.message, "error");
  } finally { $("btn-registrar").disabled = false; }
});

$("btn-login").addEventListener("click", async () => {
  $("btn-login").disabled = true;
  try {
    const u = await post("/api/login", {
      carnet_universitario: $("l-carnet").value.trim(),
      correo: $("l-correo").value.trim(),
    });
    guardarUsuario(u);
    mostrarVista();
  } catch (e) {
    setMsg("msg-login", e.message, "error");
  } finally { $("btn-login").disabled = false; }
});

$("btn-logout").addEventListener("click", cerrarSesion);

/* ═══════════════ modos de visualización ═══════════════ */
let modo = "gradiente";

const DESCRIPCIONES = {
  gradiente:
    "Escribe un campo escalar f(x, y). Se grafica la superficie z = f(x, y) y, sobre el plano, " +
    "el campo gradiente ∇f = (∂f/∂x, ∂f/∂y), que apunta en la dirección de máximo crecimiento.",
  hamiltoniano:
    "Escribe la función hamiltoniana H(x, y) (energía del sistema). Se grafica la superficie de energía " +
    "y el campo X_H = (∂H/∂y, −∂H/∂x). Las trayectorias siguen las curvas de nivel H = constante.",
  vectorial3d:
    "Define las tres componentes del campo F(x, y, z) = P i + Q j + R k. Se muestra el campo con conos 3D " +
    "y se calculan simbólicamente la divergencia ∇·F y el rotacional ∇×F.",
};

const EJEMPLOS = {
  gradiente: [
    { t: "x^2 - y^2 (silla)", f: "x^2 - y^2" },
    { t: "x^2 + y^2 (paraboloide)", f: "x^2 + y^2" },
    { t: "sin(x)*cos(y)", f: "sin(x)*cos(y)" },
    { t: "x*exp(-x^2-y^2)", f: "x*exp(-x^2 - y^2)" },
  ],
  hamiltoniano: [
    { t: "Oscilador armónico", f: "(x^2 + y^2)/2" },
    { t: "Péndulo simple", f: "y^2/2 - cos(x)" },
    { t: "Doble pozo (Duffing)", f: "y^2/2 - x^2/2 + x^4/4" },
    { t: "Silla hiperbólica", f: "x*y" },
  ],
  vectorial3d: [
    { t: "Rotación: (-y, x, z/2)", P: "-y", Q: "x", R: "z/2" },
    { t: "Radial: (x, y, z)", P: "x", Q: "y", R: "z" },
    { t: "Solenoidal: (y, -x, 0)", P: "y", Q: "-x", R: "0" },
    { t: "Cizalla: (z, 0, x)", P: "z", Q: "0", R: "x" },
  ],
};

function activarModo(nuevo) {
  modo = nuevo;
  document.querySelectorAll(".modo-tab").forEach(b =>
    b.classList.toggle("activa", b.dataset.modo === modo));
  $("modo-descripcion").textContent = DESCRIPCIONES[modo];
  const esVect = modo === "vectorial3d";
  $("entrada-escalar").classList.toggle("hidden", esVect);
  $("entrada-vectorial").classList.toggle("hidden", !esVect);
  $("lbl-f").textContent = modo === "hamiltoniano" ? "H(x, y) =" : "f(x, y) =";
  if (modo === "hamiltoniano" && !$("in-f").dataset.tocado) $("in-f").value = "y^2/2 - cos(x)";
  if (modo === "gradiente" && !$("in-f").dataset.tocado) $("in-f").value = "x^2 - y^2";
  renderEjemplos();
}

function renderEjemplos() {
  const cont = $("ejemplos");
  cont.innerHTML = "";
  EJEMPLOS[modo].forEach(ej => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "ejemplo-btn"; b.textContent = ej.t;
    b.addEventListener("click", () => {
      if (modo === "vectorial3d") {
        $("in-P").value = ej.P; $("in-Q").value = ej.Q; $("in-R").value = ej.R;
      } else {
        $("in-f").value = ej.f; $("in-f").dataset.tocado = "1";
      }
      graficar();
    });
    cont.appendChild(b);
  });
}

document.querySelectorAll(".modo-tab").forEach(b =>
  b.addEventListener("click", () => activarModo(b.dataset.modo)));
$("in-f").addEventListener("input", () => { $("in-f").dataset.tocado = "1"; });

/* ═══════════════ graficación ═══════════════ */
const LAYOUT_BASE = {
  margin: { l: 0, r: 0, t: 30, b: 0 },
  paper_bgcolor: "rgba(0,0,0,0)",
  font: { family: "Source Sans 3, sans-serif", color: "#1C3144" },
  scene: {
    xaxis: { title: "x", gridcolor: "#C9D4C6", zerolinecolor: "#1C3144" },
    yaxis: { title: "y", gridcolor: "#C9D4C6", zerolinecolor: "#1C3144" },
    zaxis: { title: "z", gridcolor: "#C9D4C6", zerolinecolor: "#1C3144" },
    aspectmode: "cube",
    camera: { eye: { x: 1.6, y: 1.4, z: 1.1 } },
  },
  legend: { orientation: "h", y: -0.05 },
};
const ESCALA = [[0, "#0E7C7B"], [0.5, "#F2B33D"], [1, "#C8401F"]];

function conosDesdeCampo2D(c, zPlano) {
  return {
    type: "cone",
    x: c.x, y: c.y, z: c.x.map(() => zPlano),
    u: c.u.map(v => v ?? 0), v: c.v.map(v => v ?? 0), w: c.u.map(() => 0),
    colorscale: ESCALA, sizemode: "scaled", sizeref: 1.6,
    showscale: true, colorbar: { title: "|v⃗|", len: 0.5 },
    name: "campo", hovertemplate: "(%{x:.2f}, %{y:.2f})<extra></extra>",
  };
}

async function graficar() {
  setMsg("msg-campo", "");
  const cuerpo = {
    tipo: modo,
    rango: parseFloat($("in-rango").value) || 3,
    densidad: parseInt($("in-densidad").value) || 12,
  };
  if (modo === "vectorial3d") {
    cuerpo.P = $("in-P").value; cuerpo.Q = $("in-Q").value; cuerpo.R = $("in-R").value;
  } else {
    cuerpo.f = $("in-f").value;
  }

  $("btn-graficar").disabled = true;
  $("btn-graficar").textContent = "Calculando…";
  try {
    const d = await post("/api/campo", cuerpo);
    const trazas = [];
    let resumen = "";

    if (d.tipo === "gradiente" || d.tipo === "hamiltoniano") {
      const s = d.superficie;
      const zs = s.z.flat().filter(v => v !== null);
      const zmin = Math.min(...zs);
      trazas.push({
        type: "surface", x: s.x, y: s.y, z: s.z,
        colorscale: "Viridis", opacity: 0.85, showscale: false,
        contours: { z: { show: true, usecolormap: true, project: { z: true } } },
        name: d.tipo === "gradiente" ? "z = f(x,y)" : "z = H(x,y)",
      });
      trazas.push(conosDesdeCampo2D(d.campo, zmin));

      resumen = d.tipo === "gradiente"
        ? `\\( f = ${d.latex.f} \\qquad \\nabla f = \\left( ${d.latex.fx},\\; ${d.latex.fy} \\right) \\)`
        : `\\( H = ${d.latex.H} \\qquad \\dot{x} = \\frac{\\partial H}{\\partial y} = ${d.latex.xdot}, ` +
          `\\quad \\dot{y} = -\\frac{\\partial H}{\\partial x} = ${d.latex.ydot} \\)`;
    } else {
      const c = d.campo3d;
      trazas.push({
        type: "cone",
        x: c.x, y: c.y, z: c.z,
        u: c.u.map(v => v ?? 0), v: c.v.map(v => v ?? 0), w: c.w.map(v => v ?? 0),
        colorscale: ESCALA, sizemode: "scaled", sizeref: 1.4,
        colorbar: { title: "|F⃗|", len: 0.6 },
        hovertemplate: "(%{x:.2f}, %{y:.2f}, %{z:.2f})<extra></extra>",
      });
      resumen =
        `\\( \\vec{F} = \\left( ${d.latex.P},\\; ${d.latex.Q},\\; ${d.latex.R} \\right) \\qquad ` +
        `\\nabla\\!\\cdot\\!\\vec{F} = ${d.latex.div} \\qquad ` +
        `\\nabla\\!\\times\\!\\vec{F} = \\left( ${d.latex.rot[0]},\\; ${d.latex.rot[1]},\\; ${d.latex.rot[2]} \\right) \\)`;
    }

    Plotly.newPlot("grafica", trazas, LAYOUT_BASE, { responsive: true, displaylogo: false });

    const cont = $("resumen-latex");
    cont.innerHTML = resumen;
    if (window.MathJax?.typesetPromise) MathJax.typesetPromise([cont]);

  } catch (e) {
    setMsg("msg-campo", e.message, "error");
  } finally {
    $("btn-graficar").disabled = false;
    $("btn-graficar").textContent = "Graficar";
  }
}

$("btn-graficar").addEventListener("click", graficar);
document.querySelectorAll(".in-func").forEach(inp =>
  inp.addEventListener("keydown", e => { if (e.key === "Enter") graficar(); }));

/* ═══════════════ inicio ═══════════════ */
activarModo("gradiente");
mostrarVista();
