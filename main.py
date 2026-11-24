from fastapi import FastAPI, HTTPException
from database import conexion_con_base_de_datos
from modelos import CrearTarea, RespuestaTarea
from datetime import date

app = FastAPI()

instancia = conexion_con_base_de_datos()

instancia.iniciar_la_base_de_datos()

@app.post("/tareas", response_model=RespuestaTarea) # CREACION DE TAREAS.

def crear_tarea(tarea: CrearTarea):
    #Crea una tarea en el sistema.
    conexion = instancia.obtener_conexion()
    el_cursor = conexion.cursor()

    #Inserto elementos a la tabla.

    el_cursor.execute( 
        "INSERT INTO tareas(descripcion,fecha_de_creacion,estado,id_usuario) VALUES (?,?,?,?)",
        (tarea.descripcion, tarea.fecha_de_creacion.isoformat(), tarea.estado, 1)

    )
    conexion.commit()
    nuevo_id = el_cursor.lastrowid #guarda el id que genero sql
    conexion.close()
    return RespuestaTarea(id_tarea = nuevo_id, descripcion = tarea.descripcion, fecha_de_creacion = tarea.fecha_de_creacion, estado = tarea.estado) 



@app.get("/tareas", response_model=list[RespuestaTarea])

def revisar_tareas():
    #Enlista todas las tareas del sistema.

    conexion = instancia.obtener_conexion()
    el_cursor = conexion.cursor()

    el_cursor.execute(
        "SELECT descripcion,fecha_de_creacion,estado,id_tarea FROM tareas",
        

    )
    filas = el_cursor.fetchall()
    conexion.close()
    tabla = [
        RespuestaTarea(
            descripcion=fila[0],
            fecha_de_creacion=fila[1],                  #Devuelve la tabla enlistada.
            estado=fila[2],
            id_tarea=fila[3],
        )
        for fila in filas
            ]
    return tabla


# ACTUALIZACION DE DATOS

@app.patch("/tareas/{id_tarea}")

def actualizar_datos(id_tarea: int, nuevo_dato: CrearTarea):
    #Actualiza una tarea en la base de datos.

    conexion = instancia.obtener_conexion()
    el_cursor = conexion.cursor()

    el_cursor.execute(
        "UPDATE tareas SET descripcion = ?, estado = ? WHERE id_tarea = ?",
        (nuevo_dato.descripcion, nuevo_dato.estado, id_tarea)

    )

    conexion.commit()
    if el_cursor.rowcount == 0:
       raise HTTPException(status_code=404, detail="Tarea no encontrada")
    conexion.close()
    return RespuestaTarea(id_tarea= id_tarea, descripcion= nuevo_dato.descripcion, fecha_de_creacion= date.today(), estado= nuevo_dato.estado)