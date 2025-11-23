from flask import Blueprint, request, jsonify
from app.services.reporte_service import ReporteService
from datetime import datetime, timedelta

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/api/reportes/ventas/periodo', methods=['GET'])
def reporte_ventas_periodo():
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            # Por defecto, último mes
            fecha_fin = datetime.now().strftime('%Y-%m-%d')
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        reporte = ReporteService.obtener_ventas_por_periodo(fecha_inicio, fecha_fin)
        
        return jsonify({
            'success': True,
            'data': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'reporte': reporte
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generando reporte de ventas: {str(e)}'
        }), 500

@reportes_bp.route('/api/reportes/productos/mas-vendidos', methods=['GET'])
def reporte_productos_mas_vendidos():
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        limite = int(request.args.get('limite', 10))
        
        if not fecha_inicio or not fecha_fin:
            fecha_fin = datetime.now().strftime('%Y-%m-%d')
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        productos = ReporteService.obtener_productos_mas_vendidos(fecha_inicio, fecha_fin, limite)
        
        return jsonify({
            'success': True,
            'data': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'productos': productos
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generando reporte de productos: {str(e)}'
        }), 500

@reportes_bp.route('/api/reportes/ventas/empleados', methods=['GET'])
def reporte_ventas_empleados():
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            fecha_fin = datetime.now().strftime('%Y-%m-%d')
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        empleados = ReporteService.obtener_ventas_por_empleado(fecha_inicio, fecha_fin)
        
        return jsonify({
            'success': True,
            'data': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'empleados': empleados
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generando reporte de empleados: {str(e)}'
        }), 500

@reportes_bp.route('/api/reportes/ventas/metodos-pago', methods=['GET'])
def reporte_ventas_metodos_pago():
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            fecha_fin = datetime.now().strftime('%Y-%m-%d')
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        metodos_pago = ReporteService.obtener_ventas_por_metodo_pago(fecha_inicio, fecha_fin)
        
        return jsonify({
            'success': True,
            'data': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'metodos_pago': metodos_pago
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generando reporte de métodos de pago: {str(e)}'
        }), 500

@reportes_bp.route('/api/reportes/inventario/estadisticas', methods=['GET'])
def reporte_estadisticas_inventario():
    try:
        estadisticas = ReporteService.obtener_estadisticas_inventario()
        
        return jsonify({
            'success': True,
            'data': estadisticas
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generando estadísticas de inventario: {str(e)}'
        }), 500