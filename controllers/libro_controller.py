"""
Controlador de libros: centraliza todas las operaciones relacionadas con libros.

En lugar de que cada ruta de Flask hable directamente con la base de datos,
pasamos por aquí. Así, si mañana cambiamos cómo buscamos libros, solo
modificamos este archivo y el resto del código sigue funcionando.
"""

from models.models import Libro, Autor, Categoria
from database import db
from sqlalchemy import or_
from sqlalchemy.orm import joinedload


class LibroController:
    """
    Maneja todas las consultas y operaciones relacionadas con libros.
    
    Este controlador se encarga de:
    - Abrir y cerrar sesiones de base de datos de forma segura
    - Cargar las relaciones (autor, categoría) de forma eficiente
    - Manejar errores sin romper la aplicación
    """

    def __init__(self):
        """
        Inicializa el controlador sin sesión abierta.
        
        La sesión se crea solo cuando la necesitamos (lazy loading),
        no cuando creamos el controlador. Esto evita mantener conexiones
        abiertas innecesariamente.
        """
        self.session = None

    def get_session(self):
        """
        Abre una sesión de base de datos solo cuando la necesitamos.
        
        Si ya tenemos una sesión abierta, la reutilizamos. Si no, creamos una nueva.
        Esto evita crear múltiples conexiones cuando hacemos varias operaciones seguidas.
        
        Returns:
            Una sesión de SQLAlchemy lista para hacer consultas.
        """
        if not self.session:
            self.session = db.get_session()
        return self.session

    def close_session(self):
        """
        Cierra la sesión actual y libera la conexión a la base de datos.
        
        Es importante cerrar las sesiones cuando terminamos de usarlas.
        Si no lo hacemos, podemos agotar el pool de conexiones y la aplicación
        dejará de responder.
        """
        if self.session:
            self.session.close()
            self.session = None

    def obtener_todos(self):
        """
        Trae todos los libros de la biblioteca con su autor y categoría ya cargados.
        
        Usamos joinedload para evitar el problema del "lazy loading": si no lo usáramos,
        cada vez que accediéramos a libro.autor o libro.categoria fuera de la sesión,
        SQLAlchemy intentaría hacer una consulta nueva y fallaría.
        
        Returns:
            Lista de todos los libros con sus relaciones cargadas. Si hay error, retorna lista vacía.
        """
        try:
            session = self.get_session()
            # joinedload carga autor y categoría en la misma consulta
            # Así, cuando accedamos a libro.autor.nombre_completo, ya está en memoria
            libros = session.query(Libro).options(
                joinedload(Libro.autor), 
                joinedload(Libro.categoria)
            ).all()
            return libros
        except Exception as e:
            # Si algo falla, no queremos que la aplicación se rompa
            # Devolvemos una lista vacía y registramos el error para depuración
            print(f"Error al obtener libros: {e}")
            return []
        finally:
            # Siempre cerramos la sesión, incluso si hubo un error
            self.close_session()

    def obtener_por_id(self, libro_id):
        """
        Busca un libro específico por su ISBN.
        
        Útil cuando sabemos exactamente qué libro queremos (por ejemplo,
        cuando el usuario hace clic en un libro de la lista).
        
        Args:
            libro_id: El ISBN del libro que queremos encontrar.
        
        Returns:
            El objeto Libro si lo encuentra, None si no existe o hay un error.
        """
        try:
            session = self.get_session()
            # Buscamos por ISBN (que es la llave primaria)
            # joinedload carga autor y categoría para que estén disponibles
            libro = session.query(Libro).options(
                joinedload(Libro.autor), 
                joinedload(Libro.categoria)
            ).filter(Libro.ISBN == libro_id).first()
            return libro
        except Exception as e:
            print(f"Error al obtener libro: {e}")
            return None
        finally:
            self.close_session()

    def buscar(self, termino_busqueda):
        """
        Busca libros que coincidan con el término en título, ISBN o nombre del autor.
        
        El usuario puede buscar por cualquier parte del título, el ISBN completo o parcial,
        o el nombre del autor. Hacemos una búsqueda flexible que encuentra coincidencias
        en cualquiera de estos campos.
        
        Args:
            termino_busqueda: El texto que el usuario escribió en el buscador.
        
        Returns:
            Lista de libros que coinciden con la búsqueda. Lista vacía si no hay resultados o hay error.
        """
        try:
            session = self.get_session()
            # Hacemos un JOIN con la tabla Autor para poder buscar en nombres y apellidos
            # or_() permite que coincida con cualquiera de las condiciones
            # like() con % al inicio y final busca coincidencias parciales
            libros = session.query(Libro).options(
                joinedload(Libro.autor), 
                joinedload(Libro.categoria)
            ).join(Autor).filter(
                or_(
                    Libro.Titulo.like(f'%{termino_busqueda}%'),
                    Libro.ISBN.like(f'%{termino_busqueda}%'),
                    Autor.Nombres.like(f'%{termino_busqueda}%'),
                    Autor.Apellidos.like(f'%{termino_busqueda}%')
                )
            ).all()
            return libros
        except Exception as e:
            print(f"Error en la búsqueda: {e}")
            return []
        finally:
            self.close_session()

    def obtener_disponibles(self):
        """
        Trae solo los libros que están disponibles para prestar.
        
        Cuando un usuario quiere pedir un préstamo, solo debemos mostrarle
        los libros que realmente puede tomar. Si un libro ya está prestado,
        no tiene sentido mostrarlo en el selector.
        
        Returns:
            Lista de libros con Disponible=True. Lista vacía si hay error.
        """
        try:
            session = self.get_session()
            # Filtramos por Disponible == True
            # También cargamos autor y categoría por si los necesitamos en la vista
            libros = session.query(Libro).options(
                joinedload(Libro.autor), 
                joinedload(Libro.categoria)
            ).filter(Libro.Disponible == True).all()
            return libros
        except Exception as e:
            print(f"Error al obtener libros disponibles: {e}")
            return []
        finally:
            self.close_session()
