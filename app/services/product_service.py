from app.database.db_connection import execute_query
from app.models.entities import Producto
from config import Config

class ProductService:
    @staticmethod
    def get_all_products():
        query = """
        SELECT p.*, 
               m.nombre_marca, 
               c.nombre as categoria_nombre,
               um.nombre_unidad_medida,
               e.nombre as estatus_nombre
        FROM productos p 
        LEFT JOIN marcas m ON p.fk_marcas = m.id_marcas
        LEFT JOIN categorias c ON p.fk_categorias = c.id_categorias
        LEFT JOIN unidades_medida um ON p.fk_unidades_medida = um.id_unidades_medida
        LEFT JOIN estatus_general e ON p.fk_estatus_general = e.id_estatus_general
        WHERE p.fk_estatus_general = ?
        ORDER BY p.nombre
        """
        results = execute_query(query, (Config.ESTATUS_ACTIVO,), fetch_all=True)
        return [Producto(**row).to_dict() for row in results] if results else []
    
    @staticmethod
    def get_product_by_id(product_id):
        query = """
        SELECT p.*, 
               m.nombre_marca, 
               c.nombre as categoria_nombre,
               um.nombre_unidad_medida,
               e.nombre as estatus_nombre
        FROM productos p 
        LEFT JOIN marcas m ON p.fk_marcas = m.id_marcas
        LEFT JOIN categorias c ON p.fk_categorias = c.id_categorias
        LEFT JOIN unidades_medida um ON p.fk_unidades_medida = um.id_unidades_medida
        LEFT JOIN estatus_general e ON p.fk_estatus_general = e.id_estatus_general
        WHERE p.id_productos = ? AND p.fk_estatus_general = ?
        """
        result = execute_query(query, (product_id, Config.ESTATUS_ACTIVO), fetch=True)
        return Producto(**result).to_dict() if result else None
    
    @staticmethod
    def get_product_stock(product_id):
        """Obtener stock actual del producto"""
        # En tu BD, necesitaríamos una vista o función para calcular stock
        # Por ahora, asumimos que hay una columna stock (aunque no la veo en tu estructura)
        query = """
        SELECT COALESCE((
            SELECT SUM(cantidad) FROM movimiento_detalles 
            WHERE fk_productos = ? AND fk_movimiento IN (
                SELECT id_movimiento FROM movimiento WHERE fk_movimiento_tipo = 1
            )
        ), 0) as stock_actual
        """
        result = execute_query(query, (product_id,), fetch=True)
        return result['stock_actual'] if result else 0
    
    @staticmethod
    def create_product(product_data):
        query = """
        INSERT INTO productos (
            nombre, codigo_barras, precio_compra, precio_venta, stock_minimo, stock_maximo,
            descripcion, fk_marcas, fk_categorias, fk_unidades_medida, fk_estatus_general
        )
        OUTPUT INSERTED.id_productos
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            product_data['nombre'],
            product_data.get('codigo_barras', ''),
            product_data['precio_compra'],
            product_data['precio_venta'],
            product_data.get('stock_minimo', 0),
            product_data.get('stock_maximo', 0),
            product_data.get('descripcion', ''),
            product_data.get('fk_marcas'),
            product_data.get('fk_categorias'),
            product_data.get('fk_unidades_medida'),
            Config.ESTATUS_ACTIVO
        )
        
        new_id = execute_query(query, params)
        return new_id
    
    @staticmethod
    def check_stock_sufficient(product_id, requested_quantity):
        """Verificar si hay stock suficiente"""
        current_stock = ProductService.get_product_stock(product_id)
        return current_stock >= requested_quantity