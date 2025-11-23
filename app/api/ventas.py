from flask import Blueprint, request, jsonify
from app.database.db_connection import execute_query
from app.services.venta_service import VentaService
from config import Config

ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/api/ventas', methods=['POST'])
def crear_venta():
    try:
        data = request.get_json()
        
        # Procesar la venta usando el servicio
        resultado = VentaService.procesar_venta(data)
        
        if resultado['success']:
            return jsonify({
                'success': True,
                'data': resultado['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error creando venta: {str(e)}'
        }), 500

@ventas_bp.route('/api/ventas', methods=['GET'])
def obtener_ventas():
    try:
        query = """
        SELECT v.*, 
               c.nombre as cliente_nombre,
               e.nombre + ' ' + e.apellido_1 as empleado_nombre,
               mp.forma_pago,
               vt.tipo_ventas,
               est.nombre as estatus_nombre
        FROM ventas v
        LEFT JOIN clientes c ON v.fk_cliente = c.id_clientes
        LEFT JOIN empleados e ON v.fk_empleados = e.id_empleados
        LEFT JOIN metodo_pago mp ON v.fk_metodo_pago = mp.id_metodo_pago
        LEFT JOIN ventas_tipo vt ON v.fk_ventas_tipo = vt.id_ventas_tipo
        LEFT JOIN estatus_general est ON v.fk_estatus_general = est.id_estatus_general
        ORDER BY v.fecha_ventas DESC
        """
        results = execute_query(query, fetch_all=True)
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo ventas: {str(e)}'
        }), 500

@ventas_bp.route('/api/ventas/<int:venta_id>', methods=['GET'])
def obtener_venta(venta_id):
    try:
        venta = VentaService.obtener_venta_completa(venta_id)
        
        if venta:
            return jsonify({
                'success': True,
                'data': venta
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Venta no encontrada'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo venta: {str(e)}'
        }), 500

@ventas_bp.route('/api/ventas/metodos-pago', methods=['GET'])
def obtener_metodos_pago():
    try:
        query = "SELECT * FROM metodo_pago WHERE fk_estatus_general = ?"
        results = execute_query(query, (Config.ESTATUS_ACTIVO,), fetch_all=True)
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo métodos de pago: {str(e)}'
        }), 500

@ventas_bp.route('/api/ventas/tipos-venta', methods=['GET'])
def obtener_tipos_venta():
    try:
        query = "SELECT * FROM ventas_tipo"
        results = execute_query(query, fetch_all=True)
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo tipos de venta: {str(e)}'
        }), 500