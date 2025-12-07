"""
Controlador de usuarios: maneja todas las operaciones relacionadas con usuarios.

Los usuarios son las personas que pueden pedir libros prestados. Este controlador
se encarga de buscar usuarios, crearlos, y mantener la integridad de los datos.
"""

from models.models import Usuario, Prestamo
from database import db
from sqlalchemy.orm import joinedload


class UsuarioController:
    """
    Gestiona las operaciones básicas de usuarios.
    
    Este controlador maneja:
    - Buscar usuarios (todos o por ID)
    - Crear nuevos usuarios
    - Mantener las sesiones de base de datos de forma segura
    """

    def __init__(self):
        """
        Inicializa el controlador sin sesión abierta.
        
        La sesión se crea solo cuando la necesitamos para evitar
        mantener conexiones abiertas innecesariamente.
        """
        self.session = None

    def get_session(self):
        """
        Abre una sesión de base de datos cuando la necesitamos.
        
        Reutiliza la sesión si ya existe, o crea una nueva si es necesario.
        Esto evita crear múltiples conexiones cuando hacemos varias operaciones.
        
        Returns:
            Una sesión de SQLAlchemy lista para hacer consultas.
        """
        if not self.session:
            self.session = db.get_session()
        return self.session

    def close_session(self):
        """
        Cierra la sesión actual y libera la conexión.
        
        Es importante cerrar las sesiones para no agotar el pool de conexiones.
        Si dejamos muchas sesiones abiertas, la aplicación puede dejar de responder.
        """
        if self.session:
            self.session.close()
            self.session = None

    def obtener_todos(self):
        """
        Trae todos los usuarios registrados en el sistema.
        
        Útil para mostrar listas de usuarios o para llenar un selector
        en un formulario (por ejemplo, al crear un préstamo).
        
        Returns:
            Lista de todos los usuarios. Lista vacía si hay error.
        """
        try:
            session = self.get_session()
            usuarios = session.query(Usuario).all()
            return usuarios
        except Exception as e:
            # Si algo falla, no queremos que la aplicación se rompa
            # Devolvemos una lista vacía y registramos el error
            print(f"Error al obtener usuarios: {e}")
            return []
        finally:
            # Siempre cerramos la sesión, incluso si hubo un error
            self.close_session()

    def buscar_por_id(self, usuario_id):
        """
        Busca un usuario específico por su ID.
        
        Útil cuando sabemos exactamente qué usuario queremos (por ejemplo,
        cuando el usuario hace clic en su perfil o cuando validamos un préstamo).
        
        Args:
            usuario_id: El ID del usuario que queremos encontrar.
        
        Returns:
            El objeto Usuario si lo encuentra, None si no existe o hay un error.
        """
        try:
            session = self.get_session()
            # Buscamos por IdUsuario (la llave primaria)
            usuario = session.query(Usuario).filter(Usuario.IdUsuario == usuario_id).first()
            return usuario
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
        finally:
            self.close_session()

    def crear(self, nombre, apellido, email):
        """
        Registra un nuevo usuario en el sistema.
        
        Cuando alguien se registra en la biblioteca, creamos un nuevo registro
        con sus datos básicos. El usuario queda activo por defecto, así que
        puede pedir préstamos inmediatamente.
        
        Si algo falla durante la creación (por ejemplo, el email ya existe
        y hay una restricción única), deshacemos los cambios (rollback) para
        mantener la consistencia de los datos.
        
        Args:
            nombre: El nombre del nuevo usuario
            apellido: El apellido del nuevo usuario
            email: El correo electrónico (opcional, puede ser None)
        
        Returns:
            Tupla (éxito, mensaje):
            - Si éxito es True, el usuario se creó correctamente
            - Si éxito es False, hubo un error y el mensaje explica qué pasó
        """
        try:
            session = self.get_session()
            # Creamos un nuevo objeto Usuario con los datos proporcionados
            nuevo_usuario = Usuario(
                Nombres=nombre,
                Apellidos=apellido,
                CorreoElectronico=email,
                UsuarioActivo=True  # Por defecto, los usuarios nuevos están activos
            )
            # Agregamos el usuario a la sesión y guardamos los cambios
            session.add(nuevo_usuario)
            session.commit()
            return True, f"Usuario {nombre} {apellido} creado con éxito."
        except Exception as e:
            # Si algo falla (error de conexión, violación de reglas, etc.),
            # deshacemos todos los cambios para que la base de datos quede
            # en el mismo estado que antes
            session.rollback()
            return False, f"Error al crear usuario: {e}"
        finally:
            # Siempre cerramos la sesión, incluso si hubo un error
            self.close_session()
