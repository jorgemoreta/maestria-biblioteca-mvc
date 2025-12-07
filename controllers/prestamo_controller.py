"""
Controlador de préstamos: maneja la lógica de negocio para prestar y devolver libros.

- Validamos que el libro esté disponible antes de prestarlo
- Actualizamos el estado del libro cuando se presta o devuelve
- Mantenemos la integridad de los datos (no podemos prestar un libro dos veces)
"""

from models.models import Prestamo, Libro, Usuario
from database import db
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload


class PrestamoController:
    """
    Gestiona todas las operaciones relacionadas con préstamos y devoluciones.
    
    Este controlador es responsable de:
    - Validar que podemos prestar un libro (está disponible, el usuario existe)
    - Crear el registro del préstamo en la base de datos
    - Actualizar el estado del libro cuando se presta o devuelve
    - Mantener la consistencia: si algo falla, deshace todos los cambios (rollback)
    """

    def __init__(self):
        """
        Inicializa el controlador sin sesión abierta.
        
        La sesión se crea bajo demanda para evitar mantener conexiones abiertas segun lo explicado por el profesor.
        """
        self.session = None

    def get_session(self):
        """
        Abre una sesión de base de datos cuando la necesitamos.
        
        Reutiliza la sesión si ya existe, o crea una nueva si es necesario.
        
        Returns:
            Una sesión de SQLAlchemy lista para hacer consultas y modificaciones.
        """
        if not self.session:
            self.session = db.get_session()
        return self.session

    def close_session(self):
        """
        Cierra la sesión actual y libera la conexión.
        
        Importante hacerlo siempre al terminar, incluso si hubo errores.
        """
        if self.session:
            self.session.close()
            self.session = None

    def crear_prestamo(self, isbn, usuario_id):
        """
        Crea un nuevo préstamo validando todas las reglas de negocio.
        
        Antes de prestar un libro, debemos verificar:
        1. Que el libro exista en la base de datos
        2. Que el libro esté disponible (no esté ya prestado)
        3. Que el usuario exista
        
        Si todo está bien, creamos el préstamo y marcamos el libro como no disponible.
        Si algo falla, deshacemos todos los cambios (rollback) para mantener la consistencia.
        
        Args:
            isbn: El ISBN del libro que se quiere prestar
            usuario_id: El ID del usuario que solicita el préstamo
        
        Returns:
            Tupla (éxito, mensaje): 
            - Si éxito es True, el préstamo se creó correctamente
            - Si éxito es False, hubo un error y el mensaje explica qué pasó
        """
        session = self.get_session()
        try:
            # Primero verificamos que el libro exista
            libro = session.query(Libro).filter(Libro.ISBN == isbn).first()
            if not libro:
                return False, "Libro no encontrado."
            
            # Verificamos que el libro esté disponible
            # Si ya está prestado, no podemos prestarlo de nuevo
            if not libro.Disponible:
                return False, f"El libro '{libro.Título}' ya está prestado."

            # Verificamos que el usuario exista
            usuario = session.query(Usuario).filter(Usuario.IdUsuario == usuario_id).first()
            if not usuario:
                return False, "Usuario no encontrado."

            # Creamos el préstamo
            # IMPORTANTE: Las columnas en SQL Server tienen acento, así que las respetamos
            nuevo_prestamo = Prestamo(
                ISBN=isbn,
                IdUsuario=usuario_id,
                FechaPréstamo=datetime.now(),  # Fecha actual
                FechaVencimiento=datetime.now() + timedelta(days=14),  # 14 días para devolverlo
                FechaDevolución=None  # Aún no se ha devuelto
            )
            
            # Marcamos el libro como no disponible
            # Así, si alguien más intenta prestarlo, veremos que ya está ocupado
            libro.Disponible = False

            # Agregamos el préstamo a la sesión y guardamos los cambios
            session.add(nuevo_prestamo)
            session.commit()
            return True, "Préstamo realizado exitosamente."

        except Exception as e:
            # Si algo falla (error de conexión, violación de reglas, etc.),
            # deshacemos todos los cambios para que la base de datos quede
            # en el mismo estado que antes
            session.rollback()
            print(f"Error al procesar préstamo: {e}")
            return False, f"Error al procesar préstamo: {e}"
        finally:
            # Siempre cerramos la sesión, incluso si hubo un error
            self.close_session()

    def devolver_libro(self, id_prestamo):
        """
        Registra la devolución de un libro y lo marca como disponible nuevamente.
        
        Cuando un usuario devuelve un libro:
        1. Verificamos que el préstamo exista
        2. Verificamos que no se haya devuelto ya (evitamos devoluciones duplicadas)
        3. Registramos la fecha de devolución
        4. Marcamos el libro como disponible para que otros puedan prestarlo
        
        Args:
            id_prestamo: El ID del préstamo que se quiere devolver
        
        Returns:
            Tupla (éxito, mensaje): Indica si la devolución se procesó correctamente
        """
        session = self.get_session()
        try:
            # Buscamos el préstamo por su ID
            prestamo = session.query(Prestamo).filter(Prestamo.IdPrestamo == id_prestamo).first()
            
            if not prestamo:
                return False, "Préstamo no encontrado."
            
            # Verificamos que el préstamo no haya sido devuelto ya
            # Si FechaDevolución tiene un valor, significa que ya se devolvió
            if prestamo.FechaDevolución:
                return False, "Este préstamo ya fue devuelto."

            # Registramos la fecha y hora actual como fecha de devolución
            prestamo.FechaDevolución = datetime.now()

            # Buscamos el libro asociado y lo marcamos como disponible
            # Ahora otros usuarios pueden pedirlo prestado
            libro = session.query(Libro).filter(Libro.ISBN == prestamo.ISBN).first()
            if libro:
                libro.Disponible = True

            # Guardamos todos los cambios
            session.commit()
            return True, "Libro devuelto correctamente. ¡Gracias!"

        except Exception as e:
            # Si algo falla, deshacemos los cambios
            session.rollback()
            return False, f"Error en devolución: {e}"
        finally:
            self.close_session()
            
    def obtener_prestamos_activos(self):
        """
        Trae todos los préstamos que aún no han sido devueltos.
        
        Un préstamo está activo si su FechaDevolución es None (vacía).
        Cargamos también el libro y el usuario para poder mostrarlos en la vista
        sin hacer consultas adicionales.
        
        Returns:
            Lista de préstamos activos con sus relaciones cargadas. Lista vacía si hay error.
        """
        try:
            session = self.get_session()
            # Filtramos por préstamos que no tienen fecha de devolución
            # joinedload carga libro y usuario en la misma consulta
            prestamos = session.query(Prestamo).options(
                joinedload(Prestamo.libro),
                joinedload(Prestamo.usuario)
            ).filter(Prestamo.FechaDevolución == None).all()
            return prestamos
        except Exception as e:
            print(f"Error al listar préstamos: {e}")
            return []
        finally:
            self.close_session()