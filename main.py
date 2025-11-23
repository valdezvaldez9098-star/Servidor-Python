from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config

# Importar blueprints
from app.api.auth import auth_bp
from app.api.productos import productos_bp
from app.api.ventas import ventas_bp
from app.api.proveedores import proveedores_bp
from app.api.clientes import clientes_bp
from app.api.inventario import inventario_bp
from app.api.empleados import empleados_bp
from app.api.reportes import reportes_bp
from app.sockets.notification_server import initialize_sockets

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    
    # Configurar CORS
    CORS(app, origins=Config.CORS_ORIGINS)
    
    # Configurar SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(empleados_bp)
    app.register_blueprint(reportes_bp)
    
    # Ruta de verificación de salud
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'POS Refaccionaria API',
            'database': 'SQL Server',
            'version': '1.0.0',
            'endpoints': {
                'auth': {
                    'login': 'POST /api/auth/login'
                },
                'productos': {
                    'listar': 'GET /api/productos',
                    'obtener': 'GET /api/productos/{id}',
                    'crear': 'POST /api/productos'
                },
                'ventas': {
                    'listar': 'GET /api/ventas',
                    'obtener': 'GET /api/ventas/{id}',
                    'crear': 'POST /api/ventas',
                    'metodos_pago': 'GET /api/ventas/metodos-pago',
                    'tipos_venta': 'GET /api/ventas/tipos-venta'
                },
                'clientes': {
                    'listar': 'GET /api/clientes',
                    'obtener': 'GET /api/clientes/{id}',
                    'crear': 'POST /api/clientes',
                    'credito': 'GET /api/clientes/{id}/credito',
                    'ventas': 'GET /api/clientes/{id}/ventas'
                },
                'proveedores': {
                    'listar': 'GET /api/proveedores',
                    'obtener': 'GET /api/proveedores/{id}',
                    'crear': 'POST /api/proveedores'
                },
                'inventario': {
                    'stock': 'GET /api/inventario/productos/{id}/stock',
                    'movimientos': 'GET /api/inventario/productos/{id}/movimientos',
                    'stock_bajo': 'GET /api/inventario/stock-bajo',
                    'ajustar': 'POST /api/inventario/ajustar',
                    'entrada': 'POST /api/inventario/entrada'
                },
                'empleados': {
                    'listar': 'GET /api/empleados',
                    'obtener': 'GET /api/empleados/{id}',
                    'crear': 'POST /api/empleados',
                    'ventas': 'GET /api/empleados/{id}/ventas'
                },
                'reportes': {
                    'ventas_periodo': 'GET /api/reportes/ventas/periodo',
                    'productos_mas_vendidos': 'GET /api/reportes/productos/mas-vendidos',
                    'ventas_empleados': 'GET /api/reportes/ventas/empleados',
                    'ventas_metodos_pago': 'GET /api/reportes/ventas/metodos-pago',
                    'estadisticas_inventario': 'GET /api/reportes/inventario/estadisticas'
                },
                'system': {
                    'health': 'GET /api/health',
                    'info': 'GET /api/system/info'
                }
            }
        })
    
    # Ruta de información del sistema
    @app.route('/api/system/info', methods=['GET'])
    def system_info():
        return jsonify({
            'name': 'POS Refaccionaria API',
            'version': '1.0.0',
            'description': 'Sistema de Punto de Venta para Refaccionaria de Bicicletas',
            'database': {
                'type': 'SQL Server',
                'name': Config.DB_NAME,
                'host': Config.DB_HOST
            },
            'features': [
                'Gestión completa de productos',
                'Procesamiento de ventas (contado y crédito)',
                'Control de inventario en tiempo real',
                'Gestión de clientes y crédito',
                'Gestión de proveedores',
                'Administración de empleados',
                'Sistema de reportes y analytics',
                'WebSockets para notificaciones en tiempo real',
                'API RESTful completa'
            ],
            'modules': [
                'Authentication',
                'Product Management',
                'Sales Processing',
                'Customer Management',
                'Supplier Management',
                'Inventory Control',
                'Employee Management',
                'Reporting System',
                'Real-time Notifications'
            ]
        })
    
    # Ruta de documentación de la API
    @app.route('/api', methods=['GET'])
    def api_documentation():
        return jsonify({
            'message': 'Bienvenido a la API de POS Refaccionaria',
            'documentation': 'Consulta /api/health para ver todos los endpoints disponibles',
            'version': '1.0.0',
            'status': 'active'
        })
    
    # Manejo de errores 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint no encontrado',
            'message': 'La ruta solicitada no existe en la API',
            'suggestion': 'Consulta /api/health para ver los endpoints disponibles'
        }), 404
    
    # Manejo de errores 500
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error inesperado en el servidor',
            'suggestion': 'Verifica los logs del servidor para más detalles'
        }), 500
    
    # Manejo de errores 405
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Método no permitido',
            'message': 'El método HTTP no está permitido para este endpoint'
        }), 405
    
    # Inicializar sockets
    initialize_sockets(socketio)
    
    return app, socketio

if __name__ == '__main__':
    try:
        app, socketio = create_app()
        
        print("=" * 70)
        print("SERVIDOR POS REFACCIONARIA - SISTEMA COMPLETO")
        print("=" * 70)
        print("[SERVER] Iniciando servidor...")
        print("[SERVER] API REST disponible en: http://localhost:5000")
        print("[SERVER] WebSockets disponible en: http://localhost:5000")
        print("")
        
        print("[ENDPOINTS PRINCIPALES]")
        print("  AUTH")
        print("    POST /api/auth/login                 - Autenticación de usuarios")
        print("")
        print("  PRODUCTOS")
        print("    GET  /api/productos                 - Listar productos")
        print("    POST /api/productos                 - Crear producto")
        print("    GET  /api/productos/{id}            - Obtener producto")
        print("")
        print("  VENTAS")
        print("    POST /api/ventas                    - Procesar venta")
        print("    GET  /api/ventas                    - Listar ventas")
        print("    GET  /api/ventas/{id}               - Obtener venta")
        print("    GET  /api/ventas/metodos-pago       - Métodos de pago")
        print("    GET  /api/ventas/tipos-venta        - Tipos de venta")
        print("")
        print("  CLIENTES")
        print("    GET  /api/clientes                  - Listar clientes")
        print("    POST /api/clientes                  - Crear cliente")
        print("    GET  /api/clientes/{id}             - Obtener cliente")
        print("    GET  /api/clientes/{id}/credito     - Información de crédito")
        print("")
        print("  INVENTARIO")
        print("    GET  /api/inventario/productos/{id}/stock     - Stock producto")
        print("    GET  /api/inventario/stock-bajo              - Productos stock bajo")
        print("    POST /api/inventario/ajustar                 - Ajustar inventario")
        print("")
        print("  EMPLEADOS")
        print("    GET  /api/empleados                 - Listar empleados")
        print("    POST /api/empleados                 - Crear empleado")
        print("    GET  /api/empleados/{id}/ventas     - Ventas por empleado")
        print("")
        print("  REPORTES")
        print("    GET  /api/reportes/ventas/periodo           - Ventas por periodo")
        print("    GET  /api/reportes/productos/mas-vendidos   - Productos más vendidos")
        print("    GET  /api/reportes/ventas/empleados         - Ventas por empleado")
        print("")
        print("  SISTEMA")
        print("    GET  /api/health                    - Estado del servidor")
        print("    GET  /api/system/info               - Información del sistema")
        print("")
        
        print("[SOCKETS DISPONIBLES]")
        print("  connect               - Conexión de cliente")
        print("  disconnect            - Desconexión de cliente")
        print("  client_identification - Identificación de cliente")
        print("  stock_update          - Actualización de stock")
        print("  new_sale              - Nueva venta procesada")
        print("  new_product           - Nuevo producto agregado")
        print("  low_stock_alert       - Alerta de stock bajo")
        print("  system_message        - Mensaje del sistema")
        print("  ping                  - Verificación de conectividad")
        print("")
        
        print("[DATABASE]")
        print(f"  Base de datos: {Config.DB_NAME}")
        print(f"  Servidor: {Config.DB_HOST}:{Config.DB_PORT}")
        print(f"  Usuario: {Config.DB_USER}")
        print("")
        
        print("[CONFIGURACIÓN]")
        print(f"  Modo debug: {'ACTIVADO' if Config.DEBUG else 'DESACTIVADO'}")
        print(f"  CORS: {Config.CORS_ORIGINS}")
        print("")
        
        print("[SERVER] Servidor listo y escuchando en puerto 5000")
        print("[SERVER] Presiona Ctrl+C para detener el servidor")
        print("=" * 70)
        
        # Iniciar servidor
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5000, 
            debug=Config.DEBUG,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        print("")
        print("[SERVER] Servidor detenido por el usuario")
        print("[SERVER] Hasta pronto!")
        
    except Exception as e:
        print("")
        print("[ERROR] Error crítico iniciando servidor:", str(e))
        print("[ERROR] Verifica la configuración:")
        print("  1. Archivo .env con las credenciales correctas")
        print("  2. SQL Server ejecutándose y accesible")
        print("  3. Puerto 5000 disponible")
        print("  4. Dependencias de Python instaladas (requirements.txt)")
        print("")
        print("[TROUBLESHOOTING]")
        print("  - Ejecuta: python -c \"import pyodbc; print('pyODBC instalado correctamente')\"")
        print("  - Verifica: netstat -an | findstr 5000")
        print("  - Revisa: SQL Server Configuration Manager")
        print("")