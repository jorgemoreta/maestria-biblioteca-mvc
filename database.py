"""
Abstracción mínima de la base de datos para compartir motor y sesiones.

SQLAlchemy necesita dos cosas principales:
1. Un "motor" (engine) que sabe cómo conectarse a la base de datos
2. Una "fábrica de sesiones" que crea conexiones cuando las necesitamos

En lugar de crear esto en cada controlador, lo hacemos una vez aquí
y todos los demás archivos lo reutilizan.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config
import urllib.parse

# Base declarativa: es la clase padre de la que heredan todos nuestros modelos
# SQLAlchemy la usa para saber qué tablas crear y cómo mapearlas
Base = declarative_base()


class Database:
    """
    Centraliza la configuración de la base de datos para todo el proyecto.
    
    En lugar de que cada controlador cree su propio motor y sesiones,
    creamos uno solo aquí y todos lo comparten. Esto evita:
    - Duplicar código de configuración
    - Abrir múltiples conexiones innecesarias
    - Tener que cambiar la conexión en muchos lugares si algo cambia
    """
    
    def __init__(self):
        """
        Preparamos la conexión a la base de datos cuando se crea la instancia.
        
        El proceso es:
        1. Pedimos la cadena de conexión a Config (ya tiene todos los datos)
        2. La convertimos al formato que SQLAlchemy entiende (URL)
        3. Creamos el motor que manejará todas las conexiones
        4. Creamos la fábrica de sesiones que usaremos para cada operación
        """
        # Obtenemos la cadena de conexión con los datos del servidor y base de datos
        # Por defecto usamos autenticación de Windows (más fácil en desarrollo local)
        raw_conn_string = Config.get_connection_string(use_windows_auth=True)
        
        # SQLAlchemy espera la cadena en formato URL, pero ODBC usa otro formato
        # urllib.parse.quote_plus convierte caracteres especiales para que la URL sea válida
        params = urllib.parse.quote_plus(raw_conn_string)
        conn_str = f'mssql+pyodbc:///?odbc_connect={params}'
        
        # Creamos el motor: es el objeto que sabe cómo hablar con SQL Server
        # echo=True hace que SQLAlchemy imprima en consola todos los SQL que ejecuta
        # Esto es útil para aprender y depurar, pero en producción podrías ponerlo en False
        self.engine = create_engine(conn_str, echo=True)
        
        # Creamos la fábrica de sesiones: cada vez que llamemos a SessionLocal(),
        # obtendremos una nueva sesión lista para usar
        # autocommit=False: nosotros controlamos cuándo guardar cambios (con commit)
        # autoflush=False: no envía cambios automáticamente, espera nuestro commit explícito
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self):
        """
        Abre una nueva sesión de base de datos.
        
        Cada operación (crear préstamo, buscar libro, etc.) necesita su propia sesión.
        La sesión es como una "conversación" con la base de datos: abrimos, hacemos
        nuestras consultas o cambios, y luego la cerramos.
        
        Returns:
            Una sesión de SQLAlchemy lista para hacer consultas y modificaciones.
        """
        return self.SessionLocal()

    def create_tables(self):
        """
        Crea todas las tablas en la base de datos si no existen.
        
        SQLAlchemy revisa todos los modelos que heredan de Base y crea las tablas
        correspondientes. Si ya existen, no hace nada (no las borra ni las modifica).
        
        Útil para inicializar la base de datos la primera vez que corremos el proyecto.
        """
        Base.metadata.create_all(bind=self.engine)


# Instancia global: la creamos una vez y todos los controladores la usan
# Así no tenemos que crear una nueva Database en cada archivo
db = Database()
