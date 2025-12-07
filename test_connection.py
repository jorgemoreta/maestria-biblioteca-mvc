
from database import db
from sqlalchemy import text

def probar_conexion():
    try:
        # Intentamos conectar al motor
        with db.engine.connect() as connection:
            # Ejecutamos una consulta simple
            result = connection.execute(text("SELECT @@VERSION"))
            version = result.fetchone()
            print("✅ ¡ÉXITO! Conexión establecida correctamente.")
            print(f"Versión de SQL Server: {version[0][:50]}...")
    except Exception as e:
        print("❌ ERROR DE CONEXIÓN:")
        print(e)

if __name__ == "__main__":
    probar_conexion()