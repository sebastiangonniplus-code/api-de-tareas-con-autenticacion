import httpx

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "PEGA_AQUI_TU_ACCESS_TOKEN"ID_TAREA = 3

headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Actualizar la tarea (PATCH /tareas/{id_tarea})
actualizar = httpx.patch(
    f"{BASE_URL}/tareas/{ID_TAREA}",
    headers=headers,
    json={"estado": "Completada"},
)
print("PATCH /tareas/3:", actualizar.status_code, actualizar.json())

# 2. Eliminar la tarea (DELETE /tareas/{id_tarea})
eliminar = httpx.delete(
    f"{BASE_URL}/tareas/{ID_TAREA}",
    headers=headers,
)
print("DELETE /tareas/3:", eliminar.status_code, eliminar.json())

# 3. Verificar que ya no aparece en GET /tareas
listar = httpx.get(f"{BASE_URL}/tareas", headers=headers)
print("GET /tareas:", listar.status_code, listar.json())