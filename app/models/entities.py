from datetime import datetime

class Producto:
    def __init__(self, id_productos=None, nombre=None, codigo_barras=None, 
                 precio_compra=0, precio_venta=0, stock_minimo=0, stock_maximo=0,
                 descripcion=None, fk_marcas=None, fk_categorias=None, 
                 fk_unidades_medida=None, fk_estatus_general=None, fk_productos_imagenes=None):
        self.id_productos = id_productos
        self.nombre = nombre
        self.codigo_barras = codigo_barras
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
        self.stock_minimo = stock_minimo
        self.stock_maximo = stock_maximo
        self.descripcion = descripcion
        self.fk_marcas = fk_marcas
        self.fk_categorias = fk_categorias
        self.fk_unidades_medida = fk_unidades_medida
        self.fk_estatus_general = fk_estatus_general
        self.fk_productos_imagenes = fk_productos_imagenes
    
    def to_dict(self):
        return {
            'id_productos': self.id_productos,
            'nombre': self.nombre,
            'codigo_barras': self.codigo_barras,
            'precio_compra': float(self.precio_compra),
            'precio_venta': float(self.precio_venta),
            'stock_minimo': self.stock_minimo,
            'stock_maximo': self.stock_maximo,
            'descripcion': self.descripcion,
            'fk_marcas': self.fk_marcas,
            'fk_categorias': self.fk_categorias,
            'fk_unidades_medida': self.fk_unidades_medida,
            'fk_estatus_general': self.fk_estatus_general,
            'fk_productos_imagenes': self.fk_productos_imagenes
        }

class Usuario:
    def __init__(self, id_usuarios=None, fk_usuario_tipo=None, fk_usuarios_permisos=None,
                 password_hash=None, activo=None, fk_empleado=None):
        self.id_usuarios = id_usuarios
        self.fk_usuario_tipo = fk_usuario_tipo
        self.fk_usuarios_permisos = fk_usuarios_permisos
        self.password_hash = password_hash
        self.activo = activo
        self.fk_empleado = fk_empleado
    
    def to_dict(self):
        return {
            'id_usuarios': self.id_usuarios,
            'fk_usuario_tipo': self.fk_usuario_tipo,
            'fk_usuarios_permisos': self.fk_usuarios_permisos,
            'activo': self.activo,
            'fk_empleado': self.fk_empleado
        }

class Venta:
    def __init__(self, id_ventas=None, folio=None, fecha_vencimiento_credito=None,
                 saldo_pendiente=0, enganche=0, fecha_ventas=None, fecha_cancelacion=None,
                 sub_total=0, impuestos=0, total_neto=0, descuentos=0, efectivo_recibido=0,
                 cambio=0, fk_ventas_tipo=None, fk_cliente=None, fk_empleados=None,
                 fk_metodo_pago=None, fk_estatus_general=None):
        self.id_ventas = id_ventas
        self.folio = folio
        self.fecha_vencimiento_credito = fecha_vencimiento_credito
        self.saldo_pendiente = saldo_pendiente
        self.enganche = enganche
        self.fecha_ventas = fecha_ventas or datetime.now()
        self.fecha_cancelacion = fecha_cancelacion
        self.sub_total = sub_total
        self.impuestos = impuestos
        self.total_neto = total_neto
        self.descuentos = descuentos
        self.efectivo_recibido = efectivo_recibido
        self.cambio = cambio
        self.fk_ventas_tipo = fk_ventas_tipo
        self.fk_cliente = fk_cliente
        self.fk_empleados = fk_empleados
        self.fk_metodo_pago = fk_metodo_pago
        self.fk_estatus_general = fk_estatus_general
        self.items = []
    
    def to_dict(self):
        return {
            'id_ventas': self.id_ventas,
            'folio': self.folio,
            'fecha_vencimiento_credito': self.fecha_vencimiento_credito.isoformat() if self.fecha_vencimiento_credito else None,
            'saldo_pendiente': float(self.saldo_pendiente),
            'enganche': float(self.enganche),
            'fecha_ventas': self.fecha_ventas.isoformat() if self.fecha_ventas else None,
            'fecha_cancelacion': self.fecha_cancelacion.isoformat() if self.fecha_cancelacion else None,
            'sub_total': float(self.sub_total),
            'impuestos': float(self.impuestos),
            'total_neto': float(self.total_neto),
            'descuentos': float(self.descuentos),
            'efectivo_recibido': float(self.efectivo_recibido),
            'cambio': float(self.cambio),
            'fk_ventas_tipo': self.fk_ventas_tipo,
            'fk_cliente': self.fk_cliente,
            'fk_empleados': self.fk_empleados,
            'fk_metodo_pago': self.fk_metodo_pago,
            'fk_estatus_general': self.fk_estatus_general,
            'items': [item.to_dict() for item in self.items]
        }

class VentaItem:
    def __init__(self, id_detalles_ventas=None, cantidad_productos=0, precio_unitario=0,
                 descuentos=0, importe_total=0, fk_productos=None, fk_ventas=None):
        self.id_detalles_ventas = id_detalles_ventas
        self.cantidad_productos = cantidad_productos
        self.precio_unitario = precio_unitario
        self.descuentos = descuentos
        self.importe_total = importe_total
        self.fk_productos = fk_productos
        self.fk_ventas = fk_ventas
    
    def to_dict(self):
        return {
            'id_detalles_ventas': self.id_detalles_ventas,
            'cantidad_productos': self.cantidad_productos,
            'precio_unitario': float(self.precio_unitario),
            'descuentos': float(self.descuentos),
            'importe_total': float(self.importe_total),
            'fk_productos': self.fk_productos,
            'fk_ventas': self.fk_ventas
        }