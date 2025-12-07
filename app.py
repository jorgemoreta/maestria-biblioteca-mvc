"""
Punto de entrada de la aplicación Flask: define todas las rutas y vistas.

Este archivo es el "director de orquesta" de la aplicación web. Aquí definimos:
- Qué URLs responden a qué funciones
- Qué controladores usar para cada operación
- Cómo mostrar los mensajes al usuario (éxito, errores)
- Qué plantillas HTML renderizar

Flask usa decoradores (@app.route) para conectar URLs con funciones Python.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from controllers.libro_controller import LibroController
from controllers.usuario_controller import UsuarioController
from controllers.prestamo_controller import PrestamoController
from datetime import datetime

# Creamos la aplicación Flask
app = Flask(__name__)


@app.context_processor
def inject_now():
    """
    Hace disponible la fecha y hora actual en todas las plantillas.
    
    Flask ejecuta esta función antes de renderizar cualquier plantilla.
    Así, en cualquier HTML podemos usar {{ now }} para mostrar la fecha actual
    sin tener que pasarla manualmente en cada ruta.
    
    Returns:
        Diccionario con 'now' que contiene la fecha y hora actual.
    """
    return {'now': datetime.now()}


# Clave secreta necesaria para usar mensajes flash (mensajes temporales al usuario)
# En producción, esto debería ser una variable de entorno, no un valor fijo
app.secret_key = 'clave_secreta_maestria'

# Creamos una instancia de cada controlador al iniciar la aplicación
# Así, todas las rutas pueden usar los mismos controladores
libro_controller = LibroController()
usuario_controller = UsuarioController()
prestamo_controller = PrestamoController()


@app.route('/')
def index():
    """
    Página de inicio de la aplicación.
    
    Muestra el menú principal desde donde el usuario puede navegar
    a las diferentes secciones (libros, préstamos, etc.).
    
    Returns:
        La plantilla HTML de la página de inicio.
    """
    return render_template('index.html')


@app.route('/libros')
def libros_lista():
    """
    Muestra una lista de todos los libros disponibles en la biblioteca.
    
    Trae todos los libros con su autor y categoría ya cargados,
    y los pasa a la plantilla para que los muestre en una tabla o lista.
    
    Returns:
        La plantilla HTML con la lista de libros.
    """
    # Pedimos al controlador todos los libros
    # El controlador se encarga de cargar las relaciones (autor, categoría)
    libros = libro_controller.obtener_todos()
    return render_template('libros/lista.html', libros=libros)


@app.route('/prestamos/nuevo', methods=['GET', 'POST'])
def prestamo_nuevo():
    """
    Muestra el formulario para crear un préstamo y procesa el envío.
    
    Esta ruta maneja dos casos:
    - GET: Muestra el formulario vacío con los selectores de libros y usuarios
    - POST: Procesa el formulario enviado, valida los datos y crea el préstamo
    
    Si el préstamo se crea exitosamente, redirige a la lista de libros.
    Si hay un error, muestra el mensaje y vuelve a mostrar el formulario.
    
    Returns:
        - Si es GET o hay error: el formulario HTML
        - Si es POST y éxito: redirección a la lista de libros
    """
    if request.method == 'POST':
        # El usuario envió el formulario, extraemos los datos
        isbn = request.form['isbn']
        usuario_id = request.form['usuario_id']

        # Pedimos al controlador que valide y cree el préstamo
        # El controlador se encarga de:
        # - Verificar que el libro exista y esté disponible
        # - Verificar que el usuario exista
        # - Crear el registro del préstamo
        # - Marcar el libro como no disponible
        exito, mensaje = prestamo_controller.crear_prestamo(isbn, usuario_id)

        if exito:
            # Todo salió bien, mostramos un mensaje de éxito y redirigimos
            flash(mensaje, 'success')
            return redirect(url_for('libros_lista'))
        else:
            # Algo falló, mostramos el mensaje de error
            # El formulario se mostrará de nuevo abajo
            flash(mensaje, 'error')

    # Si es GET (primera vez que se carga) o si hubo un error en POST,
    # mostramos el formulario
    # Preparamos las listas de libros disponibles y usuarios para los selectores
    libros = libro_controller.obtener_disponibles()
    usuarios = usuario_controller.obtener_todos()
    return render_template('prestamos/form.html', libros=libros, usuarios=usuarios)


@app.route('/prestamos')
def prestamos_lista():
    """
    Muestra una lista de todos los préstamos que aún están activos.
    
    Un préstamo está activo si no tiene fecha de devolución (FechaDevolución es None).
    Solo mostramos los préstamos que aún no se han devuelto, no el historial completo.
    
    Returns:
        La plantilla HTML con la lista de préstamos activos.
    """
    # Pedimos al controlador solo los préstamos que no se han devuelto
    # El controlador carga también el libro y el usuario para mostrarlos
    prestamos = prestamo_controller.obtener_prestamos_activos()
    return render_template('prestamos/lista.html', prestamos=prestamos)


@app.route('/prestamos/devolver/<int:id_prestamo>', methods=['POST'])
def prestamo_devolver(id_prestamo):
    """
    Procesa la devolución de un libro.
    
    Cuando el usuario hace clic en "Devolver" en la lista de préstamos,
    esta ruta recibe el ID del préstamo y le pide al controlador que:
    - Verifique que el préstamo exista
    - Verifique que no se haya devuelto ya
    - Registre la fecha de devolución
    - Marque el libro como disponible nuevamente
    
    Args:
        id_prestamo: El ID del préstamo que se quiere devolver (viene en la URL)
    
    Returns:
        Redirección a la lista de préstamos (con o sin mensaje de éxito/error).
    """
    # Pedimos al controlador que procese la devolución
    exito, mensaje = prestamo_controller.devolver_libro(id_prestamo)

    # Mostramos un mensaje al usuario (éxito o error)
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'error')

    # Redirigimos de vuelta a la lista de préstamos
    # Así el usuario ve el resultado de su acción
    return redirect(url_for('prestamos_lista'))


if __name__ == '__main__':
    """
    Inicia el servidor de desarrollo cuando ejecutamos este archivo directamente.
    
    debug=True hace que Flask recargue automáticamente cuando cambiamos el código
    y muestre mensajes de error detallados. Útil para desarrollo, pero NO para producción.
    """
    app.run(debug=True, port=5000)
