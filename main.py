from fastapi import FastAPI, HTTPException, Depends
from database import conexion_con_base_de_datos
from modelos import CrearTarea, RespuestaTarea, ActualizarTarea

app = FastAPI()

instancia = conexion_con_base_de_datos()

instancia.iniciar_la_base_de_datos()

def obtener_db():
    #Inicializa y finaliza la conexion del servidor.

    conexion = instancia.obtener_conexion()
    el_cursor = conexion.cursor()                                       #Me evita tener que colocar en cada funcion esto innecesariamente.
    try:
       yield el_cursor
    finally: 
        conexion.close()    


@app.post("/tareas", response_model=RespuestaTarea, status_code=201) # CREACION DE TAREAS.

def crear_tarea(tarea: CrearTarea, el_cursor = Depends(obtener_db)):
    #Crea una tarea en el sistema.

    el_cursor.execute( 
         "INSERT INTO tareas(descripcion,fecha_de_creacion,estado,id_usuario) VALUES (?,?,?,?)",
        (tarea.descripcion, tarea.fecha_de_creacion.isoformat(), tarea.estado, 1)
        )
    el_cursor.connection.commit()
    nuevo_id = el_cursor.lastrowid #guarda el id que genero sql
    return RespuestaTarea(id_tarea = nuevo_id, descripcion = tarea.descripcion, fecha_de_creacion = tarea.fecha_de_creacion, estado = tarea.estado) 



@app.get("/tareas", response_model=list[RespuestaTarea])

def revisar_tareas(el_cursor = Depends(obtener_db)):
    #Enlista todas las tareas del sistema.

    el_cursor.execute(
         "SELECT descripcion,fecha_de_creacion,estado,id_tarea FROM tareas",
           )
    filas = el_cursor.fetchall()
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

@app.patch("/tareas/{id_tarea}", response_model=RespuestaTarea)
def actualizar_datos(id_tarea: int, nuevo_dato: ActualizarTarea, el_cursor=Depends(obtener_db)):
    # Actualiza una tarea en la base de datos.

    el_cursor.execute(
        "SELECT descripcion, estado, fecha_de_creacion FROM tareas WHERE id_tarea = ?",
        (id_tarea,)
    )

    fila = el_cursor.fetchone()

    if fila is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    descripcion_final = (
        nuevo_dato.descripcion
        if nuevo_dato.descripcion is not None
        else fila[0]
    )

    estado_final = (
        nuevo_dato.estado
        if nuevo_dato.estado is not None
        else fila[1]
    )

    el_cursor.execute(
        "UPDATE tareas SET descripcion = ?, estado = ? WHERE id_tarea = ?",
        (descripcion_final, estado_final, id_tarea)
    )

    el_cursor.connection.commit()

    return RespuestaTarea(
        id_tarea=id_tarea,
        descripcion=descripcion_final,
        fecha_de_creacion=fila[2],
        estado=estado_final
    )

@app.delete("/tareas/{id_tarea}") 

def eliminar_tarea(id_tarea: int, el_cursor=Depends(obtener_db)):
    # Elimina una tarea de la base de datos.

    el_cursor.execute(
        "DELETE FROM tareas WHERE id_tarea = ?",
        (id_tarea,)
    )

    if el_cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    el_cursor.connection.commit()

    return {"mensaje": f"Tarea {id_tarea} eliminada correctamente"}