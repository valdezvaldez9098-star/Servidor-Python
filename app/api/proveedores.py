from flask import Blueprint, request, jsonify
from app.database.db_connection import execute_query
from config import Config

proveedores_bp = Blueprint('proveedores', __name__)

@proveedores_bp.route('/api/proveedores', methods=['GET'])
def obtener_proveedores():
    try:
        query = """
        SELECT p.*, 
               pc.nombre as categoria_nombre,
               est.nombre as estatus_nombre,
               t.telefono,
               co.correo_electronico,
               d.calle, d.colonia, d.ciudad
        FROM proveedores p
        LEFT JOIN proveedor_categorias pc ON p.fk_proveedor_cateogoria = pc.id_proveedor_categoria
        LEFT JOIN estatus_general est ON p.fk_estatus_general = est.id_estatus_general
        LEFT JOIN telefonos t ON p.fk_telefono = t.id_telefono
        LEFT JOIN correos_electronicos co ON p.fk_correo_electronico = co.id_correo_electronico
        LEFT JOIN direccion d ON p.fk_direccion = d.id_direccion
        WHERE p.fk_estatus_general = ?
        ORDER BY p.nombre
        """
        results = execute_query(query, (Config.ESTATUS_ACTIVO,), fetch_all=True)
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo proveedores: {str(e)}'
        }), 500

@proveedores_bp.route('/api/proveedores/<int:proveedor_id>', methods=['GET'])
def obtener_proveedor(proveedor_id):
    try:
        query = """
        SELECT p.*, 
               pc.nombre as categoria_nombre,
               est.nombre as estatus_nombre
        FROM proveedores p
        LEFT JOIN proveedor_categorias pc ON p.fk_proveedor_cateogoria = pc.id_proveedor_categoria
        LEFT JOIN estatus_general est ON p.fk_estatus_general = est.id_estatus_general
        WHERE p.id_proveedores = ? AND p.fk_estatus_general = ?
        """
        result = execute_query(query, (proveedor_id, Config.ESTATUS_ACTIVO), fetch=True)
        
        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Proveedor no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo proveedor: {str(e)}'
        }), 500

@proveedores_bp.route('/api/proveedores', methods=['POST'])
def crear_proveedor():
    try:
        data = request.get_json()
        
        # Crear teléfono
        telefono_query = """
        INSERT INTO telefonos (telefono, descripcion, fecha_ingreso, fk_telefonos_categoria)
        OUTPUT INSERTED.id_telefono
        VALUES (?, ?, GETDATE(), 1)
        """
        telefono_id = execute_query(telefono_query, (
            data.get('telefono'),
            f"Teléfono de {data.get('nombre')}"
        ))
        
        # Crear dirección
        direccion_query = """
        INSERT INTO direccion (calle, colonia, ciudad, estado, codigo_postal, fk_direccion_tipo)
        OUTPUT INSERTED.id_direccion
        VALUES (?, ?, ?, ?, ?, 1)
        """
        direccion_id = execute_query(direccion_query, (
            data.get('calle', ''),
            data.get('colonia', ''),
            data.get('ciudad', ''),
            data.get('estado', ''),
            data.get('codigo_postal', '')
        ))
        
        # Crear correo si se proporciona
        correo_id = None
        if data.get('correo_electronico'):
            correo_query = """
            INSERT INTO correos_electronicos (correo_electronico, fecha_ingreso, fk_correo_electronico_categoria)
            OUTPUT INSERTED.id_correo_electronico
            VALUES (?, GETDATE(), 1)
            """
            correo_id = execute_query(correo_query, (data.get('correo_electronico'),))
        
        # Crear proveedor
        proveedor_query = """
        INSERT INTO proveedores (
            nombre, rfc, fecha_ingreso, fk_telefono, 
            fk_correo_electronico, fk_direccion, fk_estatus_general, fk_proveedor_cateogoria
        )
        OUTPUT INSERTED.id_proveedores
        VALUES (?, ?, GETDATE(), ?, ?, ?, ?, ?)
        """
        proveedor_id = execute_query(proveedor_query, (
            data['nombre'],
            data.get('rfc', ''),
            telefono_id,
            correo_id,
            direccion_id,
            Config.ESTATUS_ACTIVO,
            data.get('fk_proveedor_cateogoria', 1)
        ))
        
        return jsonify({
            'success': True,
            'data': {'id_proveedores': proveedor_id}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error creando proveedor: {str(e)}'
        }), 500