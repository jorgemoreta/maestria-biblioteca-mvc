# Sistema de Gestión de Biblioteca 📚

Proyecto final de maestría que implementa un sistema completo de gestión bibliotecaria utilizando **Python**, **SQL Server** y el patrón de arquitectura **MVC**.

## 🚀 Tecnologías Utilizadas

* **Lenguaje:** Python 3.13
* **Base de Datos:** SQL Server 2022
* **ORM:** SQLAlchemy
* **Web Framework:** Flask
* **Frontend:** HTML5 + Bootstrap 5
* **Control de Versiones:** Git & GitHub

## 📋 Funcionalidades

1.  **Gestión de Catálogo:** Visualización de libros, autores y categorías.
2.  **Préstamos:** Sistema para registrar préstamos validando disponibilidad en tiempo real.
3.  **Devoluciones:** Proceso de devolución que libera el stock del libro automáticamente.
4.  **Estado:** Indicadores visuales de disponibilidad (Disponible/Prestado).

## 🛠️ Instalación y Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/jorgemoreta/maestria-biblioteca-mvc.git](https://github.com/jorgemoreta/maestria-biblioteca-mvc.git)
    cd maestria-biblioteca-mvc
    ```

2.  **Configurar Base de Datos:**
    * Ejecutar el script SQL proporcionado en SQL Server Management Studio.
    * Actualizar las credenciales en `config.py`.

3.  **Instalar dependencias:**
    ```bash
    pip install sqlalchemy pyodbc flask python-dotenv
    ```

4.  **Ejecutar la aplicación:**
    ```bash
    python app.py
    ```
    Visita `http://127.0.0.1:5000` en tu navegador.

## ✒️ Autor
**Jorge Moreta** - Proyecto de Maestría SBS 2025