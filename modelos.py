from pydantic import BaseModel, Field
from datetime import date

class CrearTarea(BaseModel):
    #Modela una tarea

    descripcion: str = Field(..., min_length=1)
    fecha_de_creacion: date = Field(default_factory=date.today) 
    estado: str = "Pendiente"


class RespuestaTarea(BaseModel):
    #Modela una respuesta a la tarea.
    
    id_tarea: int
    descripcion: str
    fecha_de_creacion: date 
    estado: str 


class ActualizarTarea(BaseModel):
    #Modela una tarea actualizada

    descripcion: str | None = None
    estado: str | None = None



class CrearUsuario(BaseModel):
    #Modela la creacion de un usuario del sistema.
    
    nombre_usuario: str = Field(..., min_length=8)
    contraseña_usuario: str = Field(..., min_length=8)    


class RespuestaUsuario(BaseModel):
    #Modela como se ve el usuario en el sistema.
    
    nombre_usuario: str
    fecha_de_creacion: date
    id_usuario: int
        