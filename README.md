# Task Tracker CLI

Una aplicación de línea de comandos (CLI) desarrollada en Python aplicando Programación Orientada a Objetos (POO) para gestionar tareas pendientes, guardando los datos de forma local en un archivo JSON y con control de versiones en Git.

## Características

- **Añadir tareas:** Creación automática de ID secuencial y registro de fecha/hora exacta.
- **Listar tareas:** Visualización en formato de lista prolija con ID, estado, descripción y fecha de creación.
- **Marcar como completada:** Actualización del estado de la tarea de `todo` a `completada` mediante su ID.
- **Eliminar tareas:** Borrado seguro de tareas individuales de la base de datos local.
- **Persistencia de datos:** Almacenamiento local automático utilizando únicamente la librería estándar de Python (`json`, `os`, `sys`, `datetime`).

## Uso

Ejecuta el script desde la terminal pasando los comandos correspondientes:

```bash
# Añadir una tarea
python task.py add "Estudiar POO en Python"

# Listar todas las tareas
python task.py list

# Marcar una tarea como completada (usando su ID)
python task.py done 1

# Eliminar una tarea (usando su ID)
python task.py delete 1