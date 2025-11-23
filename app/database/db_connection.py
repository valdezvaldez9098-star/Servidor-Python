import pyodbc
import threading
from config import Config

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        try:
            # Validar configuración primero
            Config.validate_config()
            
            # Cadena de conexión para SQL Server
            self.connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={Config.DB_HOST},{Config.DB_PORT};"
                f"DATABASE={Config.DB_NAME};"
                f"UID={Config.DB_USER};"
                f"PWD={Config.DB_PASSWORD};"
                f"Trusted_Connection=no;"
            )
            print("[DATABASE] Configuración de SQL Server lista")
            
            # Probar conexión
            self._test_connection()
            
        except Exception as e:
            print(f"[DATABASE ERROR] Error configurando SQL Server: {e}")
            raise
    
    def _test_connection(self):
        """Probar la conexión a la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            print("[DATABASE] Conexión a SQL Server verificada")
        except Exception as e:
            print(f"[DATABASE ERROR] No se pudo conectar a SQL Server: {e}")
            raise
    
    def get_connection(self):
        try:
            connection = pyodbc.connect(self.connection_string)
            return connection
        except Exception as e:
            print(f"[DATABASE ERROR] Error obteniendo conexión: {e}")
            raise

# Función helper para ejecutar queries en SQL Server
def execute_query(query, params=None, fetch=False, fetch_all=False):
    connection = None
    cursor = None
    try:
        db = DatabaseManager()
        connection = db.get_connection()
        cursor = connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Para SELECT queries
        if fetch:
            columns = [column[0] for column in cursor.description]
            row = cursor.fetchone()
            result = dict(zip(columns, row)) if row else None
        elif fetch_all:
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
        else:
            # Para INSERT, UPDATE, DELETE
            connection.commit()
            # Obtener el ID insertado (si es INSERT)
            if query.strip().upper().startswith('INSERT'):
                cursor.execute("SELECT SCOPE_IDENTITY()")
                result = cursor.fetchone()[0]
            else:
                result = cursor.rowcount
        
        return result
        
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"[QUERY ERROR] Error en query SQL Server: {e}")
        print(f"[QUERY DEBUG] Query: {query}")
        print(f"[QUERY DEBUG] Params: {params}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()