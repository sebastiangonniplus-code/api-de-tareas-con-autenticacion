const API_URL = "http://127.0.0.1:8000";
const TOKEN_KEY = "task_api_token";

const alerta = document.getElementById("alerta");
const seccionAuth = document.getElementById("seccion-auth");
const seccionTareas = document.getElementById("seccion-tareas");

const formLogin = document.getElementById("form-login");
const formRegistro = document.getElementById("form-registro");
const formTarea = document.getElementById("form-tarea");
const listaTareas = document.getElementById("lista-tareas");
const btnLogout = document.getElementById("btn-logout");

function mostrarAlerta(mensaje, tipo = "info") {
    alerta.textContent = mensaje;
    alerta.className = `alert alert-${tipo}`;
}

function ocultarAlerta() {
    alerta.className = "alert d-none";
    alerta.textContent = "";
}

function obtenerToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function guardarToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function limpiarToken() {
    localStorage.removeItem(TOKEN_KEY);
}

function actualizarVista() {
    const token = obtenerToken();
    if (token) {
        seccionAuth.classList.add("d-none");
        seccionTareas.classList.remove("d-none");
        cargarTareas();
    } else {
        seccionAuth.classList.remove("d-none");
        seccionTareas.classList.add("d-none");
        listaTareas.innerHTML = "";
    }
}

function formatearError(data, fallback) {
    if (!data) return fallback;
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
        return data.detail.map((item) => item.msg || JSON.stringify(item)).join(" | ");
    }
    return fallback;
}

async function fetchAutenticado(endpoint, opciones = {}) {
    const token = obtenerToken();
    const headers = {
        ...(opciones.headers || {}),
        Authorization: `Bearer ${token}`,
    };

    if (opciones.body && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }

    const respuesta = await fetch(`${API_URL}${endpoint}`, {
        ...opciones,
        headers,
    });

    if (respuesta.status === 401) {
        limpiarToken();
        actualizarVista();
        mostrarAlerta("Tu sesión expiró o el token no es válido. Iniciá sesión de nuevo.", "warning");
        throw new Error("No autorizado");
    }

    return respuesta;
}

formRegistro.addEventListener("submit", async (e) => {
    e.preventDefault();
    ocultarAlerta();

    const nombre_usuario = document.getElementById("reg-usuario").value.trim();
    const contraseña_usuario = document.getElementById("reg-password").value;

    try {
        const res = await fetch(`${API_URL}/usuarios`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre_usuario, contraseña_usuario }),
        });

        const data = await res.json().catch(() => null);

        if (!res.ok) {
            mostrarAlerta(formatearError(data, "No se pudo registrar el usuario."), "danger");
            return;
        }

        formRegistro.reset();
        mostrarAlerta(`Usuario "${data.nombre_usuario}" creado. Ahora podés iniciar sesión.`, "success");
    } catch {
        mostrarAlerta("Error de conexión con la API. Verificá que el servidor y CORS estén activos.", "danger");
    }
});

formLogin.addEventListener("submit", async (e) => {
    e.preventDefault();
    ocultarAlerta();

    const nombre_usuario = document.getElementById("login-usuario").value.trim();
    const contraseña_usuario = document.getElementById("login-password").value;

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre_usuario, contraseña_usuario }),
        });

        const data = await res.json().catch(() => null);

        if (!res.ok) {
            mostrarAlerta(formatearError(data, "Credenciales inválidas."), "danger");
            return;
        }

        guardarToken(data.access_token);
        formLogin.reset();
        mostrarAlerta("Sesión iniciada correctamente.", "success");
        actualizarVista();
    } catch {
        mostrarAlerta("Error de conexión con la API. Verificá que el servidor y CORS estén activos.", "danger");
    }
});

btnLogout.addEventListener("click", () => {
    limpiarToken();
    ocultarAlerta();
    actualizarVista();
});

function crearElementoTarea(tarea) {
    const item = document.createElement("div");
    item.className = "list-group-item d-flex flex-wrap justify-content-between align-items-center gap-2";

    const info = document.createElement("div");

    const titulo = document.createElement("div");
    titulo.className = "fw-semibold";
    titulo.textContent = tarea.descripcion;

    const meta = document.createElement("small");
    meta.className = "text-muted";
    meta.textContent = `Estado: ${tarea.estado} · Creada: ${tarea.fecha_de_creacion}`;

    info.appendChild(titulo);
    info.appendChild(meta);

    const acciones = document.createElement("div");
    acciones.className = "d-flex gap-2";

    const btnEstado = document.createElement("button");
    btnEstado.type = "button";
    btnEstado.className = "btn btn-sm btn-outline-primary";
    btnEstado.textContent = tarea.estado === "Completada" ? "Marcar Pendiente" : "Marcar Completada";
    btnEstado.addEventListener("click", () => {
        const nuevoEstado = tarea.estado === "Completada" ? "Pendiente" : "Completada";
        actualizarTarea(tarea.id_tarea, { estado: nuevoEstado });
    });

    const btnEliminar = document.createElement("button");
    btnEliminar.type = "button";
    btnEliminar.className = "btn btn-sm btn-outline-danger";
    btnEliminar.textContent = "Eliminar";
    btnEliminar.addEventListener("click", () => {
        eliminarTarea(tarea.id_tarea);
    });

    acciones.appendChild(btnEstado);
    acciones.appendChild(btnEliminar);

    item.appendChild(info);
    item.appendChild(acciones);

    return item;
}

async function cargarTareas() {
    try {
        const res = await fetchAutenticado("/tareas");
        const data = await res.json().catch(() => null);

        if (!res.ok) {
            mostrarAlerta(formatearError(data, "No se pudieron cargar las tareas."), "danger");
            return;
        }

        listaTareas.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            const vacio = document.createElement("div");
            vacio.className = "list-group-item text-muted text-center py-4";
            vacio.textContent = "Todavía no tenés tareas cargadas.";
            listaTareas.appendChild(vacio);
            return;
        }

        data.forEach((tarea) => {
            listaTareas.appendChild(crearElementoTarea(tarea));
        });
    } catch (err) {
        if (err.message !== "No autorizado") {
            mostrarAlerta("Error de conexión al obtener las tareas.", "danger");
        }
    }
}

formTarea.addEventListener("submit", async (e) => {
    e.preventDefault();
    ocultarAlerta();

    const descripcionInput = document.getElementById("tarea-descripcion");
    const estadoInput = document.getElementById("tarea-estado");

    const descripcion = descripcionInput.value.trim();
    const estado = estadoInput.value;

    if (!descripcion) return;

    try {
        const res = await fetchAutenticado("/tareas", {
            method: "POST",
            body: JSON.stringify({ descripcion, estado }),
        });

        const data = await res.json().catch(() => null);

        if (!res.ok) {
            mostrarAlerta(formatearError(data, "No se pudo crear la tarea."), "danger");
            return;
        }

        descripcionInput.value = "";
        estadoInput.value = "Pendiente";
        mostrarAlerta("Tarea agregada.", "success");
        await cargarTareas();
    } catch (err) {
        if (err.message !== "No autorizado") {
            mostrarAlerta("Error de conexión al crear la tarea.", "danger");
        }
    }
});

async function actualizarTarea(idTarea, payload) {
    ocultarAlerta();

    try {
        const res = await fetchAutenticado(`/tareas/${idTarea}`, {
            method: "PATCH",
            body: JSON.stringify(payload),
        });

        const data = await res.json().catch(() => null);

        if (!res.ok) {
            mostrarAlerta(formatearError(data, "No se pudo actualizar la tarea."), "danger");
            return;
        }

        mostrarAlerta("Tarea actualizada.", "success");
        await cargarTareas();
    } catch (err) {
        if (err.message !== "No autorizado") {
            mostrarAlerta("Error de conexión al actualizar la tarea.", "danger");
        }
    }
}

async function eliminarTarea(idTarea) {
    ocultarAlerta();

    try {
        const res = await fetchAutenticado(`/tareas/${idTarea}`, {
            method: "DELETE",
        });

        const data = await res.json().catch(() => null);

        if (!res.ok) {
            mostrarAlerta(formatearError(data, "No se pudo eliminar la tarea."), "danger");
            return;
        }

        mostrarAlerta(data?.mensaje || "Tarea eliminada.", "success");
        await cargarTareas();
    } catch (err) {
        if (err.message !== "No autorizado") {
            mostrarAlerta("Error de conexión al eliminar la tarea.", "danger");
        }
    }
}

actualizarVista();