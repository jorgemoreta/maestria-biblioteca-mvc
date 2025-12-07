from controllers.usuario_controller import UsuarioController
from controllers.prestamo_controller import PrestamoController
from controllers.libro_controller import LibroController

def probar_ciclo_prestamo():
    # Instanciamos los cerebros
    ctrl_usuario = UsuarioController()
    ctrl_prestamo = PrestamoController()
    ctrl_libro = LibroController()

    print("\n🏁 INICIANDO PRUEBA DE FLUJO COMPLETO")
    print("="*50)

    # PASO 1: CREAR UN USUARIO
    print("\n1️⃣  Creando usuario de prueba...")
    # Usamos un email random o único para que no falle si lo corres dos veces
    import random
    email_test = f"estudiante{random.randint(100,999)}@maestria.com"
    
    exito, mensaje = ctrl_usuario.crear("Estudiante", "Maestría", email_test)
    print(f"Resultado: {mensaje}")
    
    # Buscamos al usuario recién creado para obtener su ID
    usuario = ctrl_usuario.obtener_todos()[-1] # El último de la lista
    print(f"--> Usuario ID: {usuario.IdUsuario} ({usuario.nombre_completo})")

    # PASO 2: BUSCAR UN LIBRO DISPONIBLE
    print("\n2️⃣  Buscando libro disponible...")
    libros = ctrl_libro.obtener_disponibles()
    if not libros:
        print("❌ No hay libros para prestar. Fin de la prueba.")
        return
    
    libro_a_prestar = libros[0] # Agarramos el primero que encontremos
    isbn = libro_a_prestar.ISBN
    print(f"--> Libro seleccionado: {libro_a_prestar.Título} (ISBN: {isbn})")

    # PASO 3: REALIZAR EL PRÉSTAMO
    print(f"\n3️⃣  Intentando prestar '{libro_a_prestar.Título}' a {usuario.Nombres}...")
    exito, mensaje = ctrl_prestamo.crear_prestamo(isbn, usuario.IdUsuario)
    
    if exito:
        print(f"✅ ¡ÉXITO! {mensaje}")
    else:
        print(f"❌ FALLÓ: {mensaje}")
        return # Si falla aquí, no podemos devolverlo

    # PASO 4: VERIFICAR QUE YA NO ESTÁ DISPONIBLE
    print("\n4️⃣  Verificando inventario...")
    libro_verif = ctrl_libro.obtener_por_id(isbn)
    estado = "DISPONIBLE" if libro_verif.Disponible else "OCUPADO"
    print(f"--> Estado actual del libro: {estado}")

    # PASO 5: LISTAR PRÉSTAMOS ACTIVOS
    print("\n5️⃣  Consultando préstamos activos en sistema...")
    activos = ctrl_prestamo.obtener_prestamos_activos()
    id_prestamo_realizado = None
    
    for p in activos:
        print(f"   - Préstamo #{p.IdPrestamo}: {p.libro.Título} prestado a {p.usuario.Nombres}")
        if p.ISBN == isbn and p.IdUsuario == usuario.IdUsuario:
            id_prestamo_realizado = p.IdPrestamo

    # PASO 6: DEVOLVER EL LIBRO
    if id_prestamo_realizado:
        print(f"\n6️⃣  Devolviendo el libro (Préstamo ID: {id_prestamo_realizado})...")
        exito, mensaje = ctrl_prestamo.devolver_libro(id_prestamo_realizado)
        print(f"Resultado: {mensaje}")
        
        # Verificar que vuelve a estar disponible
        libro_final = ctrl_libro.obtener_por_id(isbn)
        print(f"--> ¿El libro está disponible de nuevo?: {libro_final.Disponible}")
    
    print("\n🏁 PRUEBA FINALIZADA")

if __name__ == "__main__":
    probar_ciclo_prestamo()