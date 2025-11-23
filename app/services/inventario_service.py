from app.database.db_connection import execute_query
from config import Config
from datetime import datetime

class InventarioService:
    
    @staticmethod
    def obtener_stock_producto(producto_id):
        """Obtener stock actual de un producto basado en movimientos"""
        try:
            query = """
            SELECT 
                COALESCE((
                    SELECT SUM(md.cantidad) 
                    FROM movimiento_detalles md
                    INNER JOIN movimiento m ON md.fk_movimiento = m.id_movimiento
                    WHERE md.fk_productos = ? AND m.fk_movimiento_tipo = 1  -- Entradas
                ), 0) -
                COALESCE((
                    SELECT SUM(md.cantidad) 
                    FROM movimiento_detalles md
                    INNER JOIN movimiento m ON md.fk_movimiento = m.id_movimiento
                    WHERE md.fk_productos = ? AND m.fk_movimiento_tipo = 2  -- Salidas
                ), 0) as stock_actual
            """
            result = execute_query(query, (producto_id, producto_id), fetch=True)
            return result['stock_actual'] if result else 0
        except Exception as e:
            print(f"[INVENTARIO] Error obteniendo stock: {e}")
            return 0
    
    @staticmethod
    def registrar_movimiento_inventario(producto_id, empleado_id, cantidad, tipo_movimiento, concepto=""):
        """Registrar movimiento de inventario"""
        try:
            # Obtener existencia anterior
            existencia_anterior = InventarioService.obtener_stock_producto(producto_id)
            existencia_nueva = existencia_anterior + cantidad if tipo_movimiento == 1 else existencia_anterior - cantidad
            
            # Insertar movimiento
            movimiento_query = """
            INSERT INTO movimiento (fk_movimiento_tipo, fk_producto)
            OUTPUT INSERTED.id_movimiento
            VALUES (?, ?)
            """
            movimiento_id = execute_query(movimiento_query, (tipo_movimiento, producto_id))
            
            # Insertar detalle de movimiento
            detalle_query = """
            INSERT INTO movimiento_detalles (
                fk_productos, fk_empleados, cantidad, existencia_anterior,
                existencia_nueva, fecha_movimiento, fk_movimiento
            )
            VALUES (?, ?, ?, ?, ?, GETDATE(), ?)
            """
            execute_query(detalle_query, (
                producto_id, empleado_id, abs(cantidad), 
                existencia_anterior, existencia_nueva, movimiento_id
            ))
            
            return True
        except Exception as e:
            print(f"[INVENTARIO] Error registrando movimiento: {e}")
            return False
    
    @staticmethod
    def obtener_movimientos_producto(producto_id, fecha_inicio=None, fecha_fin=None):
        """Obtener historial de movimientos de un producto"""
        try:
            query = """
            SELECT md.*, 
                   m.fk_movimiento_tipo,
                   mt.tipo_movimiento,
                   e.nombre + ' ' + e.apellido_1 as empleado_nombre
            FROM movimiento_detalles md
            INNER JOIN movimiento m ON md.fk_movimiento = m.id_movimiento
            INNER JOIN movimiento_tipo mt ON m.fk_movimiento_tipo = mt.id_tipo_movimiento
            INNER JOIN empleados e ON md.fk_empleados = e.id_empleados
            WHERE md.fk_productos = ?
            """
            params = [producto_id]
            
            if fecha_inicio and fecha_fin:
                query += " AND md.fecha_movimiento BETWEEN ? AND ?"
                params.extend([fecha_inicio, fecha_fin])
            
            query += " ORDER BY md.fecha_movimiento DESC"
            
            return execute_query(query, tuple(params), fetch_all=True)
        except Exception as e:
            print(f"[INVENTARIO] Error obteniendo movimientos: {e}")
            return []
    
    @staticmethod
    def obtener_productos_stock_bajo():
        """Obtener productos con stock por debajo del mínimo"""
        try:
            query = """
            SELECT p.*, 
                   COALESCE((
                       SELECT SUM(md.cantidad) 
                       FROM movimiento_detalles md
                       INNER JOIN movimiento m ON md.fk_movimiento = m.id_movimiento
                       WHERE md.fk_productos = p.id_productos AND m.fk_movimiento_tipo = 1
                   ), 0) -
                   COALESCE((
                       SELECT SUM(md.cantidad) 
                       FROM movimiento_detalles md
                       INNER JOIN movimiento m ON md.fk_movimiento = m.id_movimiento
                       WHERE md.fk_productos = p.id_productos AND m.fk_movimiento_tipo = 2
                   ), 0) as stock_actual
            FROM productos p
            WHERE p.fk_estatus_general = ?
            HAVING stock_actual <= p.stock_minimo
            """
            return execute_query(query, (Config.ESTATUS_ACTIVO,), fetch_all=True)
        except Exception as e:
            print(f"[INVENTARIO] Error obteniendo productos stock bajo: {e}")
            return []
    
    @staticmethod
    def ajustar_inventario(producto_id, empleado_id, nueva_cantidad, motivo):
        """Ajustar manualmente el inventario"""
        try:
            stock_actual = InventarioService.obtener_stock_producto(producto_id)
            diferencia = nueva_cantidad - stock_actual
            
            if diferencia == 0:
                return True, "No se requiere ajuste"
            
            tipo_movimiento = 1 if diferencia > 0 else 2  # 1 = Entrada, 2 = Salida
            
            # Registrar movimiento de ajuste
            movimiento_query = """
            INSERT INTO movimiento (fk_movimiento_tipo, fk_producto)
            OUTPUT INSERTED.id_movimiento
            VALUES (?, ?)
            """
            movimiento_id = execute_query(movimiento_query, (3, producto_id))  # 3 = Ajuste
            
            # Insertar detalle de movimiento
            detalle_query = """
            INSERT INTO movimiento_detalles (
                fk_productos, fk_empleados, cantidad, existencia_anterior,
                existencia_nueva, fecha_movimiento, fk_movimiento
            )
            VALUES (?, ?, ?, ?, ?, GETDATE(), ?)
            """
            execute_query(detalle_query, (
                producto_id, empleado_id, abs(diferencia), 
                stock_actual, nueva_cantidad, movimiento_id
            ))
            
            return True, f"Ajuste realizado: {diferencia} unidades"
        except Exception as e:
            return False, f"Error en ajuste: {str(e)}"