from database import db
from models.models import Libro

def listar_libros():
    session = db.get_session()
    try:
        # Hacemos una consulta usando el ORM (select * from tblLibros)
        libros = session.query(Libro).all()
        
        print("\n📚 LISTA DE LIBROS EN LA BIBLIOTECA:")
        print("="*50)
        for libro in libros:
            # Gracias a las relaciones, podemos acceder al nombre del autor directamente
            print(f"- {libro.Título} (Autor: {libro.autor.nombre_completo})")
            
    except Exception as e:
        print("❌ Error:", e)
    finally:
        session.close()

if __name__ == "__main__":
    listar_libros()