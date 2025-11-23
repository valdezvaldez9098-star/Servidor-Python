from app.database.db_connection import execute_query
from app.services.product_service import ProductService
from config import Config
import random
import string
from datetime import datetime, timedelta

class VentaService:
    
    @staticmethod
    def generar_folio():
        """Generar folio único para la venta"""
        letters = string.ascii_uppercase
        random_str = ''.join(random.choice(letters) for i in range(3))
        random_num = ''.join(random.choice(string.digits) for i in range(4))
        return f"VTA-{random_str}-{random_num}"
    
    @staticmethod
    def validar_stock_venta(items):
        """Validar que haya stock suficiente para todos los productos"""
        errores = []
        for item in items:
            if not ProductService.check_stock_sufficient(item['fk_productos'], item['cantidad_productos']):
                producto = ProductService.get_product_by_id(item['fk_productos'])
                nombre_producto = producto['nombre'] if producto else f"ID {item['fk_productos']}"
                errores.append(f"Stock insuficiente para {nombre_producto}")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def calcular_totales_venta(items, descuentos_generales=0):
        """Calcular subtotal, impuestos y total de la venta"""
        subtotal = 0
        
        for item in items:
            precio_unitario = item['precio_unitario']
            cantidad = item['cantidad_productos']
            descuento_item = item.get('descuentos', 0)
            
            importe_bruto = precio_unitario * cantidad
            importe_descuento = importe_bruto * (descuento_item / 100) if descuento_item > 0 else 0
            importe_neto = importe_bruto - importe_descuento
            
            subtotal += importe_neto
        
        impuestos = subtotal * 0.16  # 16% IVA
        total_neto = subtotal + impuestos - descuentos_generales
        
        return {
            'sub_total': subtotal,
            'impuestos': impuestos,
            'descuentos': descuentos_generales,
            'total_neto': total_neto
        }
    
    @staticmethod
    def procesar_venta(venta_data):
        """Procesar una venta completa"""
        connection = None
        try:
            from app.database.db_connection import DatabaseManager
            db = DatabaseManager()
            connection = db.get_connection()
            connection.autocommit = False
            
            cursor = connection.cursor()
            
            # Validar stock
            stock_valido, errores_stock = VentaService.validar_stock_venta(venta_data['items'])
            if not stock_valido:
                return {'success': False, 'error': '; '.join(errores_stock)}
            
            # Calcular totales
            totales = VentaService.calcular_totales_venta(
                venta_data['items'], 
                venta_data.get('descuentos', 0)
            )
            
            # Generar folio
            folio = VentaService.generar_folio()
            
            # Determinar fecha de vencimiento si es crédito
            fecha_vencimiento = None
            saldo_pendiente = 0
            enganche = 0
            
            if venta_data.get('fk_ventas_tipo') == 2:  # Venta a crédito
                fecha_vencimiento = datetime.now() + timedelta(days=30)  # 30 días por defecto
                saldo_pendiente = totales['total_neto']
                enganche = venta_data.get('enganche', 0)
                saldo_pendiente -= enganche
            
            # Insertar venta principal
            venta_query = """
            INSERT INTO ventas (
                folio, fecha_vencimiento_credito, saldo_pendiente, enganche,
                fecha_ventas, sub_total, impuestos, total_neto, descuentos,
                efectivo_recibido, cambio, fk_ventas_tipo, fk_cliente, 
                fk_empleados, fk_metodo_pago, fk_estatus_general
            )
            OUTPUT INSERTED.id_ventas
            VALUES (?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(venta_query, (
                folio,
                fecha_vencimiento,
                saldo_pendiente,
                enganche,
                totales['sub_total'],
                totales['impuestos'],
                totales['total_neto'],
                totales['descuentos'],
                venta_data.get('efectivo_recibido', 0),
                venta_data.get('cambio', 0),
                venta_data.get('fk_ventas_tipo', 1),  # 1 = Contado por defecto
                venta_data.get('fk_cliente'),
                venta_data['fk_empleados'],
                venta_data['fk_metodo_pago'],
                Config.ESTATUS_ACTIVO
            ))
            
            venta_id = cursor.fetchone()[0]
            
            # Insertar detalles de venta
            for item in venta_data['items']:
                descuento_item = item.get('descuentos', 0)
                importe_bruto = item['precio_unitario'] * item['cantidad_productos']
                importe_descuento = importe_bruto * (descuento_item / 100) if descuento_item > 0 else 0
                importe_total = importe_bruto - importe_descuento
                
                detalle_query = """
                INSERT INTO ventas_detalles (
                    cantidad_productos, precio_unitario, descuentos, importe_total,
                    fk_productos, fk_ventas
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(detalle_query, (
                    item['cantidad_productos'],
                    item['precio_unitario'],
                    descuento_item,
                    importe_total,
                    item['fk_productos'],
                    venta_id
                ))
                
                # Registrar movimiento de inventario
                movimiento_query = """
                INSERT INTO movimiento (fk_movimiento_tipo, fk_producto)
                OUTPUT INSERTED.id_movimiento
                VALUES (2, ?)  -- 2 = Salida por venta
                """
                cursor.execute(movimiento_query, (item['fk_productos'],))
                movimiento_id = cursor.fetchone()[0]
                
                # Obtener existencia anterior (necesitarías una función para esto)
                existencia_anterior = ProductService.get_product_stock(item['fk_productos'])
                existencia_nueva = existencia_anterior - item['cantidad_productos']
                
                # Insertar detalle de movimiento
                movimiento_detalle_query = """
                INSERT INTO movimiento_detalles (
                    fk_productos, fk_empleados, cantidad, existencia_anterior,
                    existencia_nueva, fecha_movimiento, fk_movimiento
                )
                VALUES (?, ?, ?, ?, ?, GETDATE(), ?)
                """
                cursor.execute(movimiento_detalle_query, (
                    item['fk_productos'],
                    venta_data['fk_empleados'],
                    item['cantidad_productos'],
                    existencia_anterior,
                    existencia_nueva,
                    movimiento_id
                ))
            
            # Si es venta a crédito, actualizar saldo del cliente
            if venta_data.get('fk_ventas_tipo') == 2 and venta_data.get('fk_cliente'):
                VentaService.actualizar_saldo_cliente(
                    venta_data['fk_cliente'], 
                    saldo_pendiente,
                    cursor
                )
            
            # Crear cuenta por cobrar si es crédito
            if venta_data.get('fk_ventas_tipo') == 2 and venta_data.get('fk_cliente'):
                cuenta_query = """
                INSERT INTO cuentas_por_cobrar_pagar (
                    fk_cuentas_tipo, fk_clientes, fk_ventas, monto,
                    fecha_emision, fecha_vencimiento, fk_estatus_general
                )
                VALUES (1, ?, ?, ?, GETDATE(), ?, ?)  -- 1 = Cuenta por cobrar
                """
                cursor.execute(cuenta_query, (
                    venta_data['fk_cliente'],
                    venta_id,
                    saldo_pendiente,
                    fecha_vencimiento,
                    Config.ESTATUS_ACTIVO
                ))
            
            connection.commit()
            
            return {
                'success': True,
                'data': {
                    'id_ventas': venta_id,
                    'folio': folio,
                    'totales': totales,
                    'fecha_ventas': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            if connection:
                connection.rollback()
            return {'success': False, 'error': f'Error procesando venta: {str(e)}'}
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def actualizar_saldo_cliente(cliente_id, monto_venta, cursor=None):
        """Actualizar saldo actual del cliente para ventas a crédito"""
        try:
            query = "UPDATE clientes SET saldo_actual = saldo_actual + ? WHERE id_clientes = ?"
            if cursor:
                cursor.execute(query, (monto_venta, cliente_id))
            else:
                execute_query(query, (monto_venta, cliente_id))
            return True
        except Exception as e:
            print(f"[VENTA SERVICE] Error actualizando saldo cliente: {e}")
            return False
    
    @staticmethod
    def obtener_venta_completa(venta_id):
        """Obtener información completa de una venta con sus detalles"""
        try:
            # Información de la venta principal
            venta_query = """
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
            WHERE v.id_ventas = ?
            """
            venta = execute_query(venta_query, (venta_id,), fetch=True)
            
            if not venta:
                return None
            
            # Detalles de la venta
            detalles_query = """
            SELECT vd.*, 
                   p.nombre as producto_nombre,
                   p.codigo_barras as producto_codigo
            FROM ventas_detalles vd
            LEFT JOIN productos p ON vd.fk_productos = p.id_productos
            WHERE vd.fk_ventas = ?
            """
            detalles = execute_query(detalles_query, (venta_id,), fetch_all=True)
            
            venta['detalles'] = detalles or []
            return venta
            
        except Exception as e:
            print(f"[VENTA SERVICE] Error obteniendo venta: {e}")
            return None
    
    @staticmethod
    def obtener_ventas_por_fecha(fecha_inicio, fecha_fin):
        """Obtener ventas en un rango de fechas"""
        try:
            query = """
            SELECT v.*, 
                   c.nombre as cliente_nombre,
                   e.nombre + ' ' + e.apellido_1 as empleado_nombre,
                   mp.forma_pago
            FROM ventas v
            LEFT JOIN clientes c ON v.fk_cliente = c.id_clientes
            LEFT JOIN empleados e ON v.fk_empleados = e.id_empleados
            LEFT JOIN metodo_pago mp ON v.fk_metodo_pago = mp.id_metodo_pago
            WHERE v.fecha_ventas BETWEEN ? AND ?
            ORDER BY v.fecha_ventas DESC
            """
            return execute_query(query, (fecha_inicio, fecha_fin), fetch_all=True)
        except Exception as e:
            print(f"[VENTA SERVICE] Error obteniendo ventas por fecha: {e}")
            return []