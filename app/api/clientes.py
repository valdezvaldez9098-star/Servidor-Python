from flask import Blueprint, request, jsonify
from app.database.db_connection import execute_query
from config import Config

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/api/clientes', methods=['GET'])
def obtener_clientes():
    try:
        query = """
        SELECT c.*, 
               est.nombre as estatus_nombre,
               t.telefono,
               co.correo_electronico,
               d.calle, d.colonia, d.ciudad, d.estado, d.codigo_postal
        FROM clientes c
        LEFT JOIN estatus_general est ON c.fk_estatus_general = est.id_estatus_general
        LEFT JOIN telefonos t ON c.fk_telefonos = t.id_telefono
        LEFT JOIN correos_electronicos co ON c.fk_correo_electronico = co.id_correo_electronico
        LEFT JOIN direccion d ON c.fk_direccion = d.id_direccion
        WHERE c.fk_estatus_general = ?
        ORDER BY c.nombre
        """
        results = execute_query(query, (Config.ESTATUS_ACTIVO,), fetch_all=True)
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo clientes: {str(e)}'
        }), 500

@clientes_bp.route('/api/clientes/<int:cliente_id>', methods=['GET'])
def obtener_cliente(cliente_id):
    try:
        query = """
        SELECT c.*, 
               est.nombre as estatus_nombre,
               t.telefono,
               co.correo_electronico,
               d.calle, d.colonia, d.ciudad, d.estado, d.codigo_postal
        FROM clientes c
        LEFT JOIN estatus_general est ON c.fk_estatus_general = est.id_estatus_general
        LEFT JOIN telefonos t ON c.fk_telefonos = t.id_telefono
        LEFT JOIN correos_electronicos co ON c.fk_correo_electronico = co.id_correo_electronico
        LEFT JOIN direccion d ON c.fk_direccion = d.id_direccion
        WHERE c.id_clientes = ? AND c.fk_estatus_general = ?
        """
        result = execute_query(query, (cliente_id, Config.ESTATUS_ACTIVO), fetch=True)
        
        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Cliente no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo cliente: {str(e)}'
        }), 500

@clientes_bp.route('/api/clientes', methods=['POST'])
def crear_cliente():
    try:
        data = request.get_json()
        
        # Primero crear teléfono
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
        
        # Crear cliente
        cliente_query = """
        INSERT INTO clientes (
            nombre, fk_telefonos, fk_correo_electronico, rfc, 
            limite_credito, saldo_actual, fecha_registro, fk_direccion, fk_estatus_general
        )
        OUTPUT INSERTED.id_clientes
        VALUES (?, ?, ?, ?, ?, ?, GETDATE(), ?, ?)
        """
        cliente_id = execute_query(cliente_query, (
            data['nombre'],
            telefono_id,
            correo_id,
            data.get('rfc', ''),
            data.get('limite_credito', 0),
            data.get('saldo_actual', 0),
            direccion_id,
            Config.ESTATUS_ACTIVO
        ))
        
        return jsonify({
            'success': True,
            'data': {'id_clientes': cliente_id}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error creando cliente: {str(e)}'
        }), 500

@clientes_bp.route('/api/clientes/<int:cliente_id>', methods=['PUT'])
def actualizar_cliente(cliente_id):
    try:
        data = request.get_json()
        
        query = """
        UPDATE clientes 
        SET nombre = ?, rfc = ?, limite_credito = ?
        WHERE id_clientes = ? AND fk_estatus_general = ?
        """
        execute_query(query, (
            data.get('nombre'),
            data.get('rfc'),
            data.get('limite_credito'),
            cliente_id,
            Config.ESTATUS_ACTIVO
        ))
        
        return jsonify({
            'success': True,
            'message': 'Cliente actualizado correctamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error actualizando cliente: {str(e)}'
        }), 500

@clientes_bp.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
def eliminar_cliente(cliente_id):
    try:
        query = "UPDATE clientes SET fk_estatus_general = ? WHERE id_clientes = ?"
        execute_query(query, (Config.ESTATUS_INACTIVO, cliente_id))
        
        return jsonify({
            'success': True,
            'message': 'Cliente eliminado correctamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error eliminando cliente: {str(e)}'
        }), 500

@clientes_bp.route('/api/clientes/<int:cliente_id>/credito', methods=['GET'])
def obtener_info_credito(cliente_id):
    try:
        query = """
        SELECT limite_credito, saldo_actual, 
               (limite_credito - saldo_actual) as credito_disponible
        FROM clientes 
        WHERE id_clientes = ? AND fk_estatus_general = ?
        """
        result = execute_query(query, (cliente_id, Config.ESTATUS_ACTIVO), fetch=True)
        
        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Cliente no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo información de crédito: {str(e)}'
        }), 500

@clientes_bp.route('/api/clientes/<int:cliente_id>/ventas', methods=['GET'])
def obtener_ventas_cliente(cliente_id):
    try:
        query = """
        SELECT v.*, mp.forma_pago, vt.tipo_ventas
        FROM ventas v
        LEFT JOIN metodo_pago mp ON v.fk_metodo_pago = mp.id_metodo_pago
        LEFT JOIN ventas_tipo vt ON v.fk_ventas_tipo = vt.id_ventas_tipo
        WHERE v.fk_cliente = ? AND v.fk_estatus_general = ?
        ORDER BY v.fecha_ventas DESC
        """
        results = execute_query(query, (cliente_id, Config.ESTATUS_ACTIVO), fetch_all=True)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo ventas del cliente: {str(e)}'
        }), 500