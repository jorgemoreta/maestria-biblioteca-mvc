from controllers.libro_controller import LibroController
from views.console_view import ConsoleView
import sys

class BibliotecaApp:
    def __init__(self):
        # Inicializamos los componentes del MVC
        self.libro_controller = LibroController()
        self.view = ConsoleView()

    def ejecutar(self):
        """Bucle principal de la aplicación"""
        while True:
            opcion = self.view.mostrar_menu_principal()
            
            if opcion == '1':
                self.menu_libros()
            elif opcion == '2':
                print("\n¡Hasta luego! 👋")
                sys.exit()
            else:
                self.view.mostrar_mensaje("Opción inválida, intente de nuevo.")

    def menu_libros(self):
        while True:
            opcion = self.view.mostrar_menu_libros()
            
            if opcion == '1':
                # 1. El controlador trae los datos
                libros = self.libro_controller.obtener_todos()
                # 2. La vista los muestra
                self.view.mostrar_lista_libros(libros)
                self.view.pausar()
            
            elif opcion == '2':
                termino = input("\nIngrese término de búsqueda (Título, Autor o ISBN): ")
                libros = self.libro_controller.buscar(termino)
                self.view.mostrar_lista_libros(libros)
                self.view.pausar()
                
            elif opcion == '3':
                libros = self.libro_controller.obtener_disponibles()
                self.view.mostrar_lista_libros(libros)
                self.view.pausar()
                
            elif opcion == '4':
                break # Volver al menú principal
            else:
                self.view.mostrar_mensaje("Opción no válida.")

if __name__ == "__main__":
    app = BibliotecaApp()
    app.ejecutar()