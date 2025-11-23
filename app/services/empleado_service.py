from app.database.db_connection import execute_query
from config import Config

class EmpleadoService:
    
    @staticmethod
    def obtener_empleados_activos():
        """Obtener todos los empleados activos"""
        try:
            query = """
            SELECT e.*, 
                   est.nombre as estatus_nombre,
                   t.telefono,
                   co.correo_electronico,
                   d.calle, d.colonia, d.ciudad, d.estado, d.codigo_postal,
                   u.id_usuarios,
                   ut.nombre as tipo_usuario
            FROM empleados e
            LEFT JOIN estatus_general est ON e.fk_estatus_general = est.id_estatus_general
            LEFT JOIN telefonos t ON e.fk_telefonos = t.id_telefono
            LEFT JOIN correos_electronicos co ON e.fk_correo_electronico = co.id_correo_electronico
            LEFT JOIN direccion d ON e.fk_direccion = d.id_direccion
            LEFT JOIN usuarios u ON e.fk_usuario = u.id_usuarios
            LEFT JOIN usuarios_tipos ut ON u.fk_usuario_tipo = ut.id_usuario_tipo
            WHERE e.fk_estatus_general = ?
            ORDER BY e.nombre, e.apellido_1
            """
            return execute_query(query, (Config.ESTATUS_ACTIVO,), fetch_all=True)
        except Exception as e:
            print(f"[EMPLEADO] Error obteniendo empleados: {e}")
            return []
    
    @staticmethod
    def obtener_empleado_por_id(empleado_id):
        """Obtener empleado por ID"""
        try:
            query = """
            SELECT e.*, 
                   est.nombre as estatus_nombre,
                   t.telefono,
                   co.correo_electronico,
                   d.calle, d.colonia, d.ciudad, d.estado, d.codigo_postal,
                   u.id_usuarios,
                   ut.nombre as tipo_usuario
            FROM empleados e
            LEFT JOIN estatus_general est ON e.fk_estatus_general = est.id_estatus_general
            LEFT JOIN telefonos t ON e.fk_telefonos = t.id_telefono
            LEFT JOIN correos_electronicos co ON e.fk_correo_electronico = co.id_correo_electronico
            LEFT JOIN direccion d ON e.fk_direccion = d.id_direccion
            LEFT JOIN usuarios u ON e.fk_usuario = u.id_usuarios
            LEFT JOIN usuarios_tipos ut ON u.fk_usuario_tipo = ut.id_usuario_tipo
            WHERE e.id_empleados = ? AND e.fk_estatus_general = ?
            """
            return execute_query(query, (empleado_id, Config.ESTATUS_ACTIVO), fetch=True)
        except Exception as e:
            print(f"[EMPLEADO] Error obteniendo empleado: {e}")
            return None
    
    @staticmethod
    def crear_empleado(empleado_data):
        """Crear nuevo empleado"""
        try:
            # Crear teléfono
            telefono_query = """
            INSERT INTO telefonos (telefono, descripcion, fecha_ingreso, fk_telefonos_categoria)
            OUTPUT INSERTED.id_telefono
            VALUES (?, ?, GETDATE(), 1)
            """
            telefono_id = execute_query(telefono_query, (
                empleado_data.get('telefono'),
                f"Teléfono de {empleado_data.get('nombre')} {empleado_data.get('apellido_1')}"
            ))
            
            # Crear dirección
            direccion_query = """
            INSERT INTO direccion (calle, colonia, ciudad, estado, codigo_postal, fk_direccion_tipo)
            OUTPUT INSERTED.id_direccion
            VALUES (?, ?, ?, ?, ?, 1)
            """
            direccion_id = execute_query(direccion_query, (
                empleado_data.get('calle', ''),
                empleado_data.get('colonia', ''),
                empleado_data.get('ciudad', ''),
                empleado_data.get('estado', ''),
                empleado_data.get('codigo_postal', '')
            ))
            
            # Crear correo si se proporciona
            correo_id = None
            if empleado_data.get('correo_electronico'):
                correo_query = """
                INSERT INTO correos_electronicos (correo_electronico, fecha_ingreso, fk_correo_electronico_categoria)
                OUTPUT INSERTED.id_correo_electronico
                VALUES (?, GETDATE(), 1)
                """
                correo_id = execute_query(correo_query, (empleado_data.get('correo_electronico'),))
            
            # Crear empleado
            empleado_query = """
            INSERT INTO empleados (
                nombre, apellido_1, apellido_2, rfc, curp, nss,
                fk_telefonos, fk_correo_electronico, fk_direccion, fk_estatus_general
            )
            OUTPUT INSERTED.id_empleados
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            empleado_id = execute_query(empleado_query, (
                empleado_data['nombre'],
                empleado_data.get('apellido_1', ''),
                empleado_data.get('apellido_2', ''),
                empleado_data.get('rfc', ''),
                empleado_data.get('curp', ''),
                empleado_data.get('nss', ''),
                telefono_id,
                correo_id,
                direccion_id,
                Config.ESTATUS_ACTIVO
            ))
            
            return empleado_id
        except Exception as e:
            print(f"[EMPLEADO] Error creando empleado: {e}")
            return None
    
    @staticmethod
    def obtener_ventas_empleado(empleado_id, fecha_inicio=None, fecha_fin=None):
        """Obtener ventas realizadas por un empleado"""
        try:
            query = """
            SELECT v.*, 
                   c.nombre as cliente_nombre,
                   mp.forma_pago,
                   vt.tipo_ventas
            FROM ventas v
            LEFT JOIN clientes c ON v.fk_cliente = c.id_clientes
            LEFT JOIN metodo_pago mp ON v.fk_metodo_pago = mp.id_metodo_pago
            LEFT JOIN ventas_tipo vt ON v.fk_ventas_tipo = vt.id_ventas_tipo
            WHERE v.fk_empleados = ? AND v.fk_estatus_general = ?
            """
            params = [empleado_id, Config.ESTATUS_ACTIVO]
            
            if fecha_inicio and fecha_fin:
                query += " AND v.fecha_ventas BETWEEN ? AND ?"
                params.extend([fecha_inicio, fecha_fin])
            
            query += " ORDER BY v.fecha_ventas DESC"
            
            return execute_query(query, tuple(params), fetch_all=True)
        except Exception as e:
            print(f"[EMPLEADO] Error obteniendo ventas: {e}")
            return []