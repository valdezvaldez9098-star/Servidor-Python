from flask import Blueprint, request, jsonify
from app.services.inventario_service import InventarioService
from config import Config

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/api/inventario/productos/<int:producto_id>/stock', methods=['GET'])
def obtener_stock_producto(producto_id):
    try:
        stock = InventarioService.obtener_stock_producto(producto_id)
        return jsonify({
            'success': True,
            'data': {
                'producto_id': producto_id,
                'stock_actual': stock
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo stock: {str(e)}'
        }), 500

@inventario_bp.route('/api/inventario/productos/<int:producto_id>/movimientos', methods=['GET'])
def obtener_movimientos_producto(producto_id):
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        movimientos = InventarioService.obtener_movimientos_producto(
            producto_id, fecha_inicio, fecha_fin
        )
        
        return jsonify({
            'success': True,
            'data': movimientos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo movimientos: {str(e)}'
        }), 500

@inventario_bp.route('/api/inventario/stock-bajo', methods=['GET'])
def obtener_productos_stock_bajo():
    try:
        productos = InventarioService.obtener_productos_stock_bajo()
        return jsonify({
            'success': True,
            'data': productos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo productos con stock bajo: {str(e)}'
        }), 500

@inventario_bp.route('/api/inventario/ajustar', methods=['POST'])
def ajustar_inventario():
    try:
        data = request.get_json()
        
        producto_id = data.get('producto_id')
        empleado_id = data.get('empleado_id')
        nueva_cantidad = data.get('nueva_cantidad')
        motivo = data.get('motivo', 'Ajuste manual')
        
        if not all([producto_id, empleado_id, nueva_cantidad]):
            return jsonify({
                'success': False,
                'error': 'Faltan campos requeridos: producto_id, empleado_id, nueva_cantidad'
            }), 400
        
        success, mensaje = InventarioService.ajustar_inventario(
            producto_id, empleado_id, nueva_cantidad, motivo
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': mensaje
            })
        else:
            return jsonify({
                'success': False,
                'error': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error ajustando inventario: {str(e)}'
        }), 500

@inventario_bp.route('/api/inventario/entrada', methods=['POST'])
def registrar_entrada_inventario():
    try:
        data = request.get_json()
        
        producto_id = data.get('producto_id')
        empleado_id = data.get('empleado_id')
        cantidad = data.get('cantidad')
        concepto = data.get('concepto', 'Entrada de inventario')
        
        if not all([producto_id, empleado_id, cantidad]):
            return jsonify({
                'success': False,
                'error': 'Faltan campos requeridos: producto_id, empleado_id, cantidad'
            }), 400
        
        if cantidad <= 0:
            return jsonify({
                'success': False,
                'error': 'La cantidad debe ser mayor a 0'
            }), 400
        
        success = InventarioService.registrar_movimiento_inventario(
            producto_id, empleado_id, cantidad, 1, concepto  # 1 = Entrada
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Entrada de inventario registrada correctamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error registrando entrada de inventario'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error registrando entrada: {str(e)}'
        }), 500