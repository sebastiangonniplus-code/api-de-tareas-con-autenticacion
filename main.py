from fastapi import FastAPI, HTTPException, Depends
from database import conexion_con_base_de_datos
from modelos import CrearTarea, RespuestaTarea, ActualizarTarea, CrearUsuario, RespuestaUsuario, LoguearUsuario, Token, crear_access_token
from pwdlib import PasswordHash
import sqlite3
import jwt
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError("Falta SECRET_KEY o tiene menos de 32 bytes en .env")
app = FastAPI()
password_hash = PasswordHash.recommended()
instancia = conexion_con_base_de_datos()
instancia.iniciar_la_base_de_datos()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") #Extrae el token del header bearer.

def obtener_db():
    #Inicializa y finaliza la conexion del servidor.

    conexion = instancia.obtener_conexion()
    el_cursor = conexion.cursor()                                       #Me evita tener que colocar en cada funcion esto innecesariamente.
    try:
       yield el_cursor
    finally: 
        conexion.close()    





#Sistema de creacion de usuario#

@app.post("/usuarios", response_model=RespuestaUsuario, status_code=201)

def crear_Usuario(usuario: CrearUsuario, el_cursor = Depends(obtener_db)):
    #Crea un usuario en el sistema.
    
    contraseña_hasheada = password_hash.hash(usuario.contraseña_usuario)
    try:
        el_cursor.execute(
        "INSERT INTO usuarios(nombre_usuario,contraseña_usuario,fecha_de_creacion) VALUES (?,?,?)",
        (usuario.nombre_usuario, contraseña_hasheada, usuario.fecha_de_creacion.isoformat())
        ) 

        el_cursor.connection.commit()

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="El nombre de usuario ya existe")    
    
    nuevo_id = el_cursor.lastrowid #guarda el id que genero sql
    return RespuestaUsuario(nombre_usuario = usuario.nombre_usuario, fecha_de_creacion = usuario.fecha_de_creacion, id_usuario = nuevo_id)





##Sistema de Login##

@app.post("/login", response_model=Token, status_code=200)

def loguear_usuario(loguear: LoguearUsuario, el_cursor = Depends(obtener_db)):
    #Loguea el usuario en el sistema.

    el_cursor.execute(
        "SELECT id_usuario, contraseña_usuario FROM usuarios WHERE nombre_usuario = ?",
        (loguear.nombre_usuario,)
    )

    fila = el_cursor.fetchone()
    
    if fila is None or not password_hash.verify(loguear.contraseña_usuario, fila["contraseña_usuario"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = crear_access_token({"sub": str(fila["id_usuario"])}, SECRET_KEY)
    return Token(access_token=token, token_type="bearer")

def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    #Revisa que el token sea correcto.

    try:
        datos = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token expiro")
    
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="El token es invalido")

    id_usuario = datos.get("sub")
    if id_usuario is None:
        raise HTTPException(status_code=401, detail="Token inválido o sin sujeto")

    try:
        return int(id_usuario)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Token inválido o sin sujeto")




#Sistema CRUD#

@app.post("/tareas", response_model=RespuestaTarea, status_code=201) # CREACION DE TAREAS.

def crear_tarea(tarea: CrearTarea, el_cursor = Depends(obtener_db), usuario_id: int = Depends(obtener_usuario_actual)):
    #Crea una tarea en el sistema.

    el_cursor.execute( 
         "INSERT INTO tareas(descripcion,fecha_de_creacion,estado,id_usuario) VALUES (?,?,?,?)",
        (tarea.descripcion, tarea.fecha_de_creacion.isoformat(), tarea.estado, usuario_id)
        )
    el_cursor.connection.commit()
    nuevo_id = el_cursor.lastrowid #guarda el id que genero sql
    return RespuestaTarea(id_tarea = nuevo_id, descripcion = tarea.descripcion, fecha_de_creacion = tarea.fecha_de_creacion, estado = tarea.estado) 



@app.get("/tareas", response_model=list[RespuestaTarea])

def revisar_tareas(el_cursor = Depends(obtener_db), usuario_id: int = Depends(obtener_usuario_actual)):
    #Enlista todas las tareas del sistema.

    el_cursor.execute(
         "SELECT descripcion,fecha_de_creacion,estado,id_tarea FROM tareas WHERE id_usuario = ?",
           (usuario_id,)
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
def actualizar_datos(id_tarea: int, nuevo_dato: ActualizarTarea, el_cursor=Depends(obtener_db),usuario_id: int = Depends(obtener_usuario_actual)):
    # Actualiza una tarea en la base de datos.

    el_cursor.execute(
        "SELECT descripcion, estado, fecha_de_creacion FROM tareas WHERE id_tarea = ? AND id_usuario =?",
        (id_tarea,usuario_id)
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
        "UPDATE tareas SET descripcion = ?, estado = ? WHERE id_tarea = ? AND id_usuario = ?",
        (descripcion_final, estado_final, id_tarea, usuario_id)
    )

    el_cursor.connection.commit()

    return RespuestaTarea(
        id_tarea=id_tarea,
        descripcion=descripcion_final,
        fecha_de_creacion=fila[2],
        estado=estado_final
    )

@app.delete("/tareas/{id_tarea}") 

def eliminar_tarea(id_tarea: int, el_cursor=Depends(obtener_db),usuario_id: int = Depends(obtener_usuario_actual)):
    # Elimina una tarea de la base de datos.

    el_cursor.execute(
        "DELETE FROM tareas WHERE id_tarea = ? AND id_usuario = ?",
        (id_tarea,usuario_id)
    )

    if el_cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    el_cursor.connection.commit()

    return {"mensaje": f"Tarea {id_tarea} eliminada correctamente"}