import sqlite3

class conexion_con_base_de_datos():
    #Modela la conexion con la base de datos.

    def __init__(self, base_de_datos="tareas.db"):
        self.base_de_datos = base_de_datos

    def obtener_conexion(self):
        #Crea la conexion con la base de datos.

        conexion = sqlite3.connect(self.base_de_datos)
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA foreign_keys = ON")
        return conexion

    def iniciar_la_base_de_datos(self):
        #Inicializa la base de datos

        conexion = self.obtener_conexion()
        el_cursor = conexion.cursor()

        el_cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario  INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT UNIQUE NOT NULL,
            contraseña_usuario TEXT NOT NULL,
            fecha_de_creacion TEXT NOT NULL
            )
             """ )
        
        el_cursor.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
            id_tarea INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            fecha_de_creacion TEXT NOT NULL,
            estado TEXT NOT NULL,
            id_usuario INTEGER NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
            )
             """ )
        conexion.commit()
        conexion.close()


# Prueba de la conexion con la base de datos.
if __name__ == "__main__":
    db = conexion_con_base_de_datos()
    db.iniciar_la_base_de_datos()
    print("Base de datos inicializada correctamente.")