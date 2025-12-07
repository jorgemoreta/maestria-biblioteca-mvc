"""
Modelos de datos que representan las tablas de la base de datos.

Cada clase aquí es un "molde" que SQLAlchemy usa para:
- Crear las tablas en la base de datos
- Mapear filas de la base de datos a objetos de Python
- Establecer relaciones entre tablas (qué autor escribió qué libros, etc.)

Cuando trabajamos con estos modelos, no escribimos SQL directamente:
creamos objetos Python y SQLAlchemy se encarga de traducirlos a SQL.
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Autor(Base):
    """
    Representa a una persona que escribió uno o más libros.
    
    Cada libro tiene un autor, pero un autor puede tener muchos libros.
    Por ejemplo: Gabriel García Márquez escribió "Cien años de soledad" y "El amor en los tiempos del cólera".
    """
    __tablename__ = 'tblAutores'
    
    # La llave primaria se genera automáticamente cuando creamos un nuevo autor
    IdAutor = Column(Integer, primary_key=True, autoincrement=True)
    
    # Información básica del autor
    Nombres = Column(String(100), nullable=False)  # No puede estar vacío
    Apellidos = Column(String(100), nullable=False)
    Nacionalidad = Column(String(100), nullable=False)
    OtrosDetalles = Column(Text, nullable=True)  # Puede estar vacío (biografía, premios, etc.)

    # Relación: desde un autor podemos acceder a todos sus libros
    # back_populates hace que la relación funcione en ambos sentidos
    libros = relationship("Libro", back_populates="autor")

    @property
    def nombre_completo(self):
        """
        Combina nombres y apellidos en un solo string.
        
        En lugar de escribir autor.Nombres + " " + autor.Apellidos cada vez,
        podemos hacer autor.nombre_completo y Python lo calcula automáticamente.
        """
        return f"{self.Nombres} {self.Apellidos}"

class Categoria(Base):
    """
    Representa un género o categoría de libros (Novela, Ciencia Ficción, Historia, etc.).
    
    Los libros se agrupan por categoría para facilitar la búsqueda y organización.
    Una categoría puede tener muchos libros, pero cada libro pertenece a una sola categoría.
    """
    # IMPORTANTE: La tabla en SQL Server tiene tilde en la í, así que debemos respetarlo
    __tablename__ = 'tblCategorías'
    
    # IMPORTANTE: Las columnas también tienen tildes para coincidir con la base de datos
    IdCategoría = Column(Integer, primary_key=True, autoincrement=True)
    Descripción = Column(String(100), nullable=False)  # Ejemplo: "Novela", "Ciencia Ficción"
    OtrosDetalles = Column(Text, nullable=True)

    # Relación: desde una categoría podemos ver todos los libros que pertenecen a ella
    libros = relationship("Libro", back_populates="categoria")

class Libro(Base):
    """
    Representa un libro físico en la biblioteca.
    
    Este es el modelo central: todo gira alrededor de los libros.
    Cada libro tiene un autor, una categoría, y puede estar prestado o disponible.
    """
    __tablename__ = 'tblLibros'
    
    # El ISBN es único para cada libro, así que lo usamos como llave primaria
    # No se genera automáticamente, debemos proporcionarlo al crear el libro
    ISBN = Column(String(20), primary_key=True)
    
    # Información básica del libro
    Título = Column(String(200), nullable=False)
    Publicación = Column(String(100), nullable=False)  # Nombre de la editorial
    FechaPublicación = Column(Date, nullable=False)  # Fecha en que se publicó
    
    # Llaves foráneas: conectan este libro con su autor y categoría
    # ForeignKey le dice a SQLAlchemy que estos valores deben existir en las otras tablas
    # IMPORTANTE: Usamos tildes para coincidir con los nombres reales en SQL Server
    IdCategoría = Column(Integer, ForeignKey('tblCategorías.IdCategoría'), nullable=False)
    IdAutor = Column(Integer, ForeignKey('tblAutores.IdAutor'), nullable=False)
    
    # Campos opcionales
    OtrosDetalles = Column(Text, nullable=True)  # Sinopsis, notas adicionales, etc.
    
    # Control de disponibilidad: si está en True, el libro puede prestarse
    # Si está en False, significa que alguien ya lo tiene prestado
    Disponible = Column(Boolean, default=True)

    # Relaciones: desde un libro podemos acceder a su autor, categoría y préstamos
    autor = relationship("Autor", back_populates="libros")
    categoria = relationship("Categoria", back_populates="libros")
    prestamos = relationship("Prestamo", back_populates="libro")

class Usuario(Base):
    """
    Representa a una persona que puede pedir libros prestados.
    
    Antes de prestar un libro, necesitamos saber quién lo está pidiendo.
    Un usuario puede tener múltiples préstamos (aunque no simultáneos del mismo libro).
    """
    __tablename__ = 'tblUsuarios'
    
    # ID único que se genera automáticamente
    IdUsuario = Column(Integer, primary_key=True, autoincrement=True)
    
    # Información personal
    Nombres = Column(String(100), nullable=False)
    Apellidos = Column(String(100), nullable=False)
    Direccion = Column(String(200), nullable=True)  # Opcional
    CorreoElectronico = Column(String(100), nullable=True)  # Opcional
    
    # Control de estado: si un usuario está inactivo, no debería poder pedir préstamos
    UsuarioActivo = Column(Boolean, default=True)

    # Relación: desde un usuario podemos ver todos sus préstamos (pasados y actuales)
    prestamos = relationship("Prestamo", back_populates="usuario")

    @property
    def nombre_completo(self):
        """
        Combina nombres y apellidos para mostrarlos juntos.
        
        Útil cuando necesitamos mostrar el nombre completo en listas o formularios.
        """
        return f"{self.Nombres} {self.Apellidos}"

class Prestamo(Base):
    """
    Registra cada vez que un usuario toma un libro prestado.
    
    Este modelo es el "historial" de préstamos. Cada vez que alguien pide un libro,
    creamos un registro aquí. Cuando lo devuelve, actualizamos la fecha de devolución.
    
    Si FechaDevolución está vacía (None), significa que el préstamo sigue activo.
    """
    __tablename__ = 'tblPrestamos'
    
    # ID único del préstamo
    IdPrestamo = Column(Integer, primary_key=True, autoincrement=True)
    
    # Referencias a quién pidió el préstamo y qué libro
    IdUsuario = Column(Integer, ForeignKey('tblUsuarios.IdUsuario'), nullable=False)
    ISBN = Column(String(20), ForeignKey('tblLibros.ISBN'), nullable=False)
    
    # Fechas importantes del préstamo
    # IMPORTANTE: Las columnas en SQL Server tienen tildes, así que las respetamos
    FechaPréstamo = Column(DateTime, default=datetime.now)  # Se llena automáticamente cuando creamos el préstamo
    FechaVencimiento = Column(DateTime, nullable=False)  # Cuándo debe devolverlo (ej: 14 días después)
    FechaDevolución = Column(DateTime, nullable=True)  # Si está vacía, el préstamo sigue activo
    
    # Si el usuario se pasa de la fecha de vencimiento, puede haber una multa
    MultaPagar = Column(Numeric(10, 2), nullable=True, default=0)
    
    # Notas adicionales sobre el préstamo (opcional)
    OtrosDetalles = Column(Text, nullable=True)

    # Relaciones: desde un préstamo podemos acceder al libro y al usuario
    libro = relationship("Libro", back_populates="prestamos")
    usuario = relationship("Usuario", back_populates="prestamos")