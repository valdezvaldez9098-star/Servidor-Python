import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración de SQL Server
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'sa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'POS_Refaccionaria')
    DB_PORT = os.getenv('DB_PORT', '1433')
    
    # Configuración Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave_por_defecto_no_segura')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Configuración CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Estatus general (según tu BD)
    ESTATUS_ACTIVO = 1
    ESTATUS_INACTIVO = 2