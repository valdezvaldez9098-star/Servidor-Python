from flask import Blueprint, request, jsonify
from app.database.db_connection import execute_query
from app.models.entities import Usuario
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        usuario = data.get('usuario')  # Esto sería el ID o nombre de usuario
        password = data.get('password')
        
        if not usuario or not password:
            return jsonify({
                'success': False,
                'error': 'Usuario y contraseña son requeridos'
            }), 400
        
        # Buscar usuario - necesitamos saber cómo se relaciona con empleados
        query = """
        SELECT u.*, e.nombre, e.apellido_1, e.apellido_2
        FROM usuarios u
        LEFT JOIN empleados e ON u.fk_empleado = e.id_empleados
        WHERE u.id_usuarios = ? OR u.fk_empleado IN (
            SELECT id_empleados FROM empleados WHERE nombre = ?
        )
        AND u.activo = 1
        """
        result = execute_query(query, (usuario, usuario), fetch=True)
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 401
        
        # Verificar contraseña (encriptada)
        # Nota: En producción deberíamos usar hashing
        if result['password_hash'] != password:
            return jsonify({
                'success': False,
                'error': 'Contraseña incorrecta'
            }), 401
        
        user_data = {
            'id_usuarios': result['id_usuarios'],
            'nombre_completo': f"{result['nombre']} {result['apellido_1']} {result.get('apellido_2', '')}",
            'fk_usuario_tipo': result['fk_usuario_tipo'],
            'fk_empleado': result['fk_empleado'],
            'activo': result['activo']
        }
        
        return jsonify({
            'success': True,
            'data': user_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error en login: {str(e)}'
        }), 500