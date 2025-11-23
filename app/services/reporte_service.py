from app.database.db_connection import execute_query
from config import Config
from datetime import datetime, timedelta

class ReporteService:
    
    @staticmethod
    def obtener_ventas_por_periodo(fecha_inicio, fecha_fin):
        """Obtener reporte de ventas por periodo"""
        try:
            query = """
            SELECT 
                COUNT(*) as total_ventas,
                SUM(v.total_neto) as total_ingresos,
                AVG(v.total_neto) as promedio_venta,
                SUM(v.impuestos) as total_impuestos,
                SUM(v.descuentos) as total_descuentos,
                COUNT(CASE WHEN v.fk_ventas_tipo = 1 THEN 1 END) as ventas_contado,
                COUNT(CASE WHEN v.fk_ventas_tipo = 2 THEN 1 END) as ventas_credito,
                SUM(CASE WHEN v.fk_ventas_tipo = 1 THEN v.total_neto ELSE 0 END) as ingresos_contado,
                SUM(CASE WHEN v.fk_ventas_tipo = 2 THEN v.total_neto ELSE 0 END) as ingresos_credito
            FROM ventas v
            WHERE v.fecha_ventas BETWEEN ? AND ?
            AND v.fk_estatus_general = ?
            """
            return execute_query(query, (fecha_inicio, fecha_fin, Config.ESTATUS_ACTIVO), fetch=True)
        except Exception as e:
            print(f"[REPORTE] Error obteniendo ventas por periodo: {e}")
            return {}
    
    @staticmethod
    def obtener_productos_mas_vendidos(fecha_inicio, fecha_fin, limite=10):
        """Obtener productos más vendidos"""
        try:
            query = """
            SELECT 
                p.id_productos,
                p.nombre,
                p.codigo_barras,
                SUM(vd.cantidad_productos) as total_vendido,
                SUM(vd.importe_total) as total_ingresos,
                COUNT(DISTINCT vd.fk_ventas) as veces_vendido
            FROM ventas_detalles vd
            INNER JOIN productos p ON vd.fk_productos = p.id_productos
            INNER JOIN ventas v ON vd.fk_ventas = v.id_ventas
            WHERE v.fecha_ventas BETWEEN ? AND ?
            AND v.fk_estatus_general = ?
            GROUP BY p.id_productos, p.nombre, p.codigo_barras
            ORDER BY total_vendido DESC
            LIMIT ?
            """
            return execute_query(query, (fecha_inicio, fecha_fin, Config.ESTATUS_ACTIVO, limite), fetch_all=True)
        except Exception as e:
            print(f"[REPORTE] Error obteniendo productos más vendidos: {e}")
            return []
    
    @staticmethod
    def obtener_ventas_por_empleado(fecha_inicio, fecha_fin):
        """Obtener ventas por empleado"""
        try:
            query = """
            SELECT 
                e.id_empleados,
                e.nombre + ' ' + e.apellido_1 as empleado_nombre,
                COUNT(v.id_ventas) as total_ventas,
                SUM(v.total_neto) as total_ingresos,
                AVG(v.total_neto) as promedio_venta
            FROM ventas v
            INNER JOIN empleados e ON v.fk_empleados = e.id_empleados
            WHERE v.fecha_ventas BETWEEN ? AND ?
            AND v.fk_estatus_general = ?
            GROUP BY e.id_empleados, e.nombre, e.apellido_1
            ORDER BY total_ingresos DESC
            """
            return execute_query(query, (fecha_inicio, fecha_fin, Config.ESTATUS_ACTIVO), fetch_all=True)
        except Exception as e:
            print(f"[REPORTE] Error obteniendo ventas por empleado: {e}")
            return []
    
    @staticmethod
    def obtener_ventas_por_metodo_pago(fecha_inicio, fecha_fin):
        """Obtener ventas por método de pago"""
        try:
            query = """
            SELECT 
                mp.id_metodo_pago,
                mp.forma_pago,
                COUNT(v.id_ventas) as total_ventas,
                SUM(v.total_neto) as total_ingresos
            FROM ventas v
            INNER JOIN metodo_pago mp ON v.fk_metodo_pago = mp.id_metodo_pago
            WHERE v.fecha_ventas BETWEEN ? AND ?
            AND v.fk_estatus_general = ?
            GROUP BY mp.id_metodo_pago, mp.forma_pago
            ORDER BY total_ingresos DESC
            """
            return execute_query(query, (fecha_inicio, fecha_fin, Config.ESTATUS_ACTIVO), fetch_all=True)
        except Exception as e:
            print(f"[REPORTE] Error obteniendo ventas por método pago: {e}")
            return []
    
    @staticmethod
    def obtener_estadisticas_inventario():
        """Obtener estadísticas de inventario"""
        try:
            query = """
            SELECT 
                COUNT(*) as total_productos,
                COUNT(CASE WHEN p.fk_estatus_general = ? THEN 1 END) as productos_activos,
                SUM(CASE 
                    WHEN (
                        SELECT COALESCE(SUM(md.cantidad), 0) 
                        FROM movimiento_detalles md
                        INNER JOIN movimiento m ON md.fk_movimiento = m.id_movimiento
                        WHERE md.fk_productos = p.id_productos AND m.fk_movimiento_tipo = 1
                    ) - 
                    COALESCE((
                        SELECT SUM(md.cantidad) 
                        FROM movimiento_detalles md
                        INNER JOIN movimiento m ON md.fk_movimiento = m.id_movimiento
                        WHERE md.fk_productos = p.id_productos AND m.fk_movimiento_tipo = 2
                    ), 0) <= p.stock_minimo THEN 1 ELSE 0 
                END) as productos_stock_bajo,
                SUM(p.precio_venta * (
                    SELECT COALESCE(SUM(md.cantidad), 0) 
                    FROM movimiento_detalles md
                    INNER JOIN movimiento m ON md.fk_movimiento = m.id_movimiento
                    WHERE md.fk_productos = p.id_productos AND m.fk_movimiento_tipo = 1
                ) - 
                COALESCE((
                    SELECT SUM(md.cantidad) 
                    FROM movimiento_detalles md
                    INNER JOIN movimiento m ON md.fk_movimiento = m.id_movimiento
                    WHERE md.fk_productos = p.id_productos AND m.fk_movimiento_tipo = 2
                ), 0)) as valor_inventario_estimado
            FROM productos p
            WHERE p.fk_estatus_general = ?
            """
            return execute_query(query, (Config.ESTATUS_ACTIVO, Config.ESTATUS_ACTIVO), fetch=True)
        except Exception as e:
            print(f"[REPORTE] Error obteniendo estadísticas inventario: {e}")
            return {}