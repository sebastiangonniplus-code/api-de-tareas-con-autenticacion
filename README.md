# api-de-tareas-con-autenticacion

API REST de gestión de tareas desarrollada con **FastAPI**, **Pydantic** y **SQLite**, con autenticación mediante **JWT** (`PyJWT`) y hashing seguro de contraseñas con **pwdlib**. Cada usuario gestiona de forma aislada sus propias tareas.

## Características

- Registro de usuarios (`POST /usuarios`) con contraseñas hasheadas y control de duplicados (`409`).
- Autenticación con JWT (`POST /login`) usando `SECRET_KEY` validada desde `.env` (mínimo 32 bytes).
- CRUD completo de tareas protegido por token Bearer:
  - `POST /tareas` — Crear tarea asociada al usuario autenticado.
  - `GET /tareas` — Listar tareas del usuario autenticado.
  - `PATCH /tareas/{id_tarea}` — Actualizar descripción o estado de una tarea propia.
  - `DELETE /tareas/{id_tarea}` — Eliminar una tarea propia.
- Persistencia en **SQLite** (`tareas.db`) con claves foráneas activas (`PRAGMA foreign_keys = ON`).

## Requisitos e instalación

1. Clonar el repositorio y entrar a la carpeta del proyecto:
   ```bash
   git clone [https://github.com/sebastiangonniplus-code/python-task-cli.git](https://github.com/sebastiangonniplus-code/python-task-cli.git)
   cd python-task-cli

2. Crear y activar un entorno virtual (venv), e instalar dependencias:
   ```bash
    python -m venv venv
    source venv/Scripts/activate   # En Windows (Git Bash)
    pip install fastapi uvicorn pydantic PyJWT pwdlib python-dotenv 

3. Configurar las variables de entorno creando un archivo .env en la raíz (no subir este archivo a Git):
    
    SECRET_KEY=tu_clave_segura_de_al_menos_32_bytes

    Podés generar una clave segura ejecutando:
       ```bash
     python -c "import secrets; print(secrets.token_hex(32))"


    Ejecución

    Levantar el servidor de desarrollo con uvicorn:
       ```bash
    uvicorn main:app --reload

    La documentación interactiva (Swagger UI) queda disponible en http://127.0.0.1:8000/docs.     