from flask import Blueprint, request, jsonify
from app.services.empleado_service import EmpleadoService
from config import Config

empleados_bp = Blueprint('empleados', __name__)

@empleados_bp.route('/api/empleados', methods=['GET'])
def obtener_empleados():
    try:
        empleados = EmpleadoService.obtener_empleados_activos()
        return jsonify({
            'success': True,
            'data': empleados
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo empleados: {str(e)}'
        }), 500

@empleados_bp.route('/api/empleados/<int:empleado_id>', methods=['GET'])
def obtener_empleado(empleado_id):
    try:
        empleado = EmpleadoService.obtener_empleado_por_id(empleado_id)
        
        if empleado:
            return jsonify({
                'success': True,
                'data': empleado
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Empleado no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo empleado: {str(e)}'
        }), 500

@empleados_bp.route('/api/empleados', methods=['POST'])
def crear_empleado():
    try:
        data = request.get_json()
        
        campos_requeridos = ['nombre', 'apellido_1', 'rfc', 'telefono']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {campo}'
                }), 400
        
        empleado_id = EmpleadoService.crear_empleado(data)
        
        if empleado_id:
            return jsonify({
                'success': True,
                'data': {'id_empleados': empleado_id}
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error creando empleado'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error creando empleado: {str(e)}'
        }), 500

@empleados_bp.route('/api/empleados/<int:empleado_id>/ventas', methods=['GET'])
def obtener_ventas_empleado(empleado_id):
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        ventas = EmpleadoService.obtener_ventas_empleado(
            empleado_id, fecha_inicio, fecha_fin
        )
        
        return jsonify({
            'success': True,
            'data': ventas
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo ventas del empleado: {str(e)}'
        }), 500

@empleados_bp.route('/api/empleados/<int:empleado_id>', methods=['PUT'])
def actualizar_empleado(empleado_id):
    try:
        data = request.get_json()
        
        query = """
        UPDATE empleados 
        SET nombre = ?, apellido_1 = ?, apellido_2 = ?, rfc = ?, curp = ?, nss = ?
        WHERE id_empleados = ? AND fk_estatus_general = ?
        """
        execute_query(query, (
            data.get('nombre'),
            data.get('apellido_1'),
            data.get('apellido_2', ''),
            data.get('rfc'),
            data.get('curp', ''),
            data.get('nss', ''),
            empleado_id,
            Config.ESTATUS_ACTIVO
        ))
        
        return jsonify({
            'success': True,
            'message': 'Empleado actualizado correctamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error actualizando empleado: {str(e)}'
        }), 500

@empleados_bp.route('/api/empleados/<int:empleado_id>', methods=['DELETE'])
def eliminar_empleado(empleado_id):
    try:
        query = "UPDATE empleados SET fk_estatus_general = ? WHERE id_empleados = ?"
        execute_query(query, (Config.ESTATUS_INACTIVO, empleado_id))
        
        return jsonify({
            'success': True,
            'message': 'Empleado eliminado correctamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error eliminando empleado: {str(e)}'
        }), 500