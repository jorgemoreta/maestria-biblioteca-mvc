from controllers.libro_controller import LibroController

def probar_controlador():
    controller = LibroController()
    
    print("\n--- PRUEBA 1: OBTENER TODOS ---")
    libros = controller.obtener_todos()
    for l in libros:
        print(f"📚 {l.Título} ({l.ISBN})")

    print("\n--- PRUEBA 2: BUSCAR 'García' ---")
    resultados = controller.buscar("García")
    for l in resultados:
        print(f"🔍 Encontrado: {l.Título} - Autor: {l.autor.nombre_completo}")

if __name__ == "__main__":
    probar_controlador()