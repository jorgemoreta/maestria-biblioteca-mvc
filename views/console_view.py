class ConsoleView:
    """Vista de consola para interacción con el usuario"""

    @staticmethod
    def mostrar_menu_principal():
        print("\n" + "="*50)
        print("   SISTEMA DE GESTIÓN DE BIBLIOTECA")
        print("="*50)
        print("1. Gestión de Libros")
        print("2. Salir")
        print("-" * 50)
        return input("Seleccione una opción: ")

    @staticmethod
    def mostrar_menu_libros():
        print("\n" + "-"*40)
        print("   GESTIÓN DE LIBROS")
        print("-" * 40)
        print("1. Listar todos los libros")
        print("2. Buscar Libro")
        print("3. Ver libros disponibles")
        print("4. Volver al menú principal")
        print("-" * 40)
        return input("Seleccione una opción: ")

    @staticmethod
    def mostrar_lista_libros(libros):
        if not libros:
            print("\n❌ No se encontraron libros.")
            return

        print("\n" + "="*100)
        # Ajustamos el formato para que se vea ordenado en columnas
        print(f"{'ISBN':<15} {'TÍTULO':<35} {'AUTOR':<25} {'CATEGORÍA':<15}")
        print("-" * 100)
        
        for libro in libros:
            # Usamos los atributos de tus modelos (Título, Descripción de categoría, etc.)
            cat_desc = libro.categoria.Descripción if libro.categoria else "N/A"
            autor_nombre = libro.autor.nombre_completo if libro.autor else "N/A"
            
            print(f"{libro.ISBN:<15} {libro.Título[:34]:<35} {autor_nombre[:24]:<25} {cat_desc[:14]:<15}")
        print("=" * 100)

    @staticmethod
    def mostrar_mensaje(mensaje):
        print(f"\nℹ️  {mensaje}")

    @staticmethod
    def pausar():
        input("\nPresione Enter para continuar...")