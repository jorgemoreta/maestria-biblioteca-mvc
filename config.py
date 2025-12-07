"""
Configuración centralizada para conectarnos a SQL Server.

En lugar de repetir los datos de conexión en cada archivo, los guardamos aquí.
Así, si cambiamos de servidor o base de datos, solo modificamos un lugar.
"""

import os


class Config:
    """
    Guarda todos los datos necesarios para conectarnos a la base de datos.
    
    Al tener todo en un solo lugar, evitamos que cada controlador o modelo
    tenga que saber cómo armar la cadena de conexión. Si mañana cambiamos
    de servidor, solo editamos estos valores.
    """
    
    # Nombre del servidor donde está corriendo SQL Server
    # El formato 'LOCALHOST\\SQLEXPRESS' es para la instancia Express local
    SERVER = 'LOCALHOST\\SQLEXPRESS'
    
    # Nombre de la base de datos que creamos para el proyecto
    DATABASE = 'BibliotecaDB'
    
    # Driver ODBC que usa Python para comunicarse con SQL Server
    # Este driver debe estar instalado en tu máquina
    DRIVER = '{ODBC Driver 17 for SQL Server}'
    
    # Credenciales para autenticación SQL Server (usuario/contraseña)
    # Solo se usan si elegimos NO usar autenticación de Windows
    USERNAME = 'sa'  # Cambiar según tu configuración
    PASSWORD = 'tu_password'  # Cambiar según tu configuración
    
    @staticmethod
    def get_connection_string(use_windows_auth=True):
        """
        Construye la cadena de conexión que SQL Server necesita para saber cómo conectarse.
        
        SQL Server puede autenticarte de dos formas:
        - Con tu usuario de Windows (más fácil para desarrollo local)
        - Con usuario y contraseña de SQL Server (más común en producción)
        
        Esta función arma la cadena en el formato que ODBC espera, dependiendo
        de qué método de autenticación queramos usar.
        
        Args:
            use_windows_auth: Si es True, usa tu usuario de Windows. Si es False, usa USERNAME/PASSWORD.
        
        Returns:
            Una cadena de texto con todos los parámetros de conexión en formato ODBC.
        """
        if use_windows_auth:
            # Usamos autenticación de Windows: SQL Server confía en que ya estás logueado
            # No necesitamos pasar usuario ni contraseña
            return (
                f"DRIVER={Config.DRIVER};"
                f"SERVER={Config.SERVER};"
                f"DATABASE={Config.DATABASE};"
                "Trusted_Connection=yes;"
            )
        else:
            # Usamos autenticación SQL Server: debemos proporcionar usuario y contraseña
            return (
                f"DRIVER={Config.DRIVER};"
                f"SERVER={Config.SERVER};"
                f"DATABASE={Config.DATABASE};"
                f"UID={Config.USERNAME};"
                f"PWD={Config.PASSWORD};"
            )
