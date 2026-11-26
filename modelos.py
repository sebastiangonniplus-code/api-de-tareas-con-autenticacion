from pydantic import BaseModel, Field
from datetime import date, datetime, timezone, timedelta
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "clave-temporal-desarrollo")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

def crear_access_token(datos: dict):
    #Da acceso tras loguear.
     
     payload = datos.copy() 
     expiracion = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
     payload["exp"] = expiracion
     return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


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
    fecha_de_creacion: date = Field(default_factory=date.today) 



class RespuestaUsuario(BaseModel):
    #Modela como se ve el usuario en el sistema.
    
    nombre_usuario: str
    fecha_de_creacion: date
    id_usuario: int


class LoguearUsuario(BaseModel):
    #Modela el logueo del usuario.

    nombre_usuario: str
    contraseña_usuario: str    
        