from flask_socketio import SocketIO, emit
from flask import request
import threading
import json

class NotificationServer:
    def __init__(self, socketio):
        self.socketio = socketio
        self.clients = set()
        self.lock = threading.Lock()
        
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.socketio.on('connect')
        def handle_connect():
            with self.lock:
                self.clients.add(request.sid)
            print(f"[SOCKET] Cliente conectado: {request.sid}")
            print(f"[SOCKET] Clientes conectados: {len(self.clients)}")
            
            # Confirmar conexión al cliente
            emit('connection_status', {
                'status': 'connected', 
                'message': 'Conectado al servidor de notificaciones',
                'clients_count': len(self.clients)
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            with self.lock:
                if request.sid in self.clients:
                    self.clients.remove(request.sid)
            print(f"[SOCKET] Cliente desconectado: {request.sid}")
            print(f"[SOCKET] Clientes conectados: {len(self.clients)}")
        
        @self.socketio.on('client_identification')
        def handle_client_identification(data):
            client_type = data.get('type', 'unknown')
            client_name = data.get('name', 'Unknown')
            
            print(f"[SOCKET] Cliente identificado: {client_name} ({client_type})")
            
            with self.lock:
                # Podrías almacenar más información del cliente si es necesario
                pass
            
            emit('identification_confirmed', {
                'status': 'identified',
                'message': f'Cliente {client_name} identificado correctamente'
            })
        
        @self.socketio.on('stock_update')
        def handle_stock_update(data):
            product_id = data.get('product_id')
            new_stock = data.get('new_stock')
            reason = data.get('reason', '')
            
            print(f"[SOCKET] Actualización de stock - Producto: {product_id}, Nuevo stock: {new_stock}, Razón: {reason}")
            
            # Notificar a todos los clientes conectados
            with self.lock:
                for client in self.clients:
                    emit('stock_updated', {
                        'product_id': product_id,
                        'new_stock': new_stock,
                        'reason': reason,
                        'timestamp': data.get('timestamp')
                    }, room=client)
        
        @self.socketio.on('new_sale')
        def handle_new_sale(data):
            sale_id = data.get('sale_id')
            total = data.get('total')
            client_name = data.get('client_name', 'N/A')
            
            print(f"[SOCKET] Nueva venta procesada - ID: {sale_id}, Total: {total}, Cliente: {client_name}")
            
            # Notificar a todos los clientes (excepto al que envió la venta)
            with self.lock:
                for client in self.clients:
                    if client != request.sid:  # No notificar al remitente
                        emit('sale_processed', {
                            'sale_id': sale_id,
                            'total': total,
                            'client_name': client_name,
                            'timestamp': data.get('timestamp'),
                            'message': f'Nueva venta procesada: ${total}'
                        }, room=client)
        
        @self.socketio.on('new_product')
        def handle_new_product(data):
            product_id = data.get('product_id')
            product_name = data.get('product_name')
            
            print(f"[SOCKET] Nuevo producto agregado - ID: {product_id}, Nombre: {product_name}")
            
            # Notificar a todos los clientes
            with self.lock:
                for client in self.clients:
                    emit('product_created', {
                        'product_id': product_id,
                        'product_name': product_name,
                        'timestamp': data.get('timestamp'),
                        'message': f'Nuevo producto: {product_name}'
                    }, room=client)
        
        @self.socketio.on('low_stock_alert')
        def handle_low_stock_alert(data):
            product_id = data.get('product_id')
            product_name = data.get('product_name')
            current_stock = data.get('current_stock')
            min_stock = data.get('min_stock')
            
            print(f"[SOCKET] Alerta de stock bajo - Producto: {product_name}, Stock: {current_stock}, Mínimo: {min_stock}")
            
            # Notificar a todos los clientes administrativos
            with self.lock:
                for client in self.clients:
                    emit('low_stock_warning', {
                        'product_id': product_id,
                        'product_name': product_name,
                        'current_stock': current_stock,
                        'min_stock': min_stock,
                        'timestamp': data.get('timestamp'),
                        'message': f'Stock bajo: {product_name} ({current_stock} unidades)'
                    }, room=client)
        
        @self.socketio.on('system_message')
        def handle_system_message(data):
            message = data.get('message', '')
            message_type = data.get('type', 'info')
            
            print(f"[SOCKET] Mensaje del sistema - Tipo: {message_type}, Mensaje: {message}")
            
            # Broadcast a todos los clientes
            with self.lock:
                for client in self.clients:
                    emit('system_notification', {
                        'message': message,
                        'type': message_type,
                        'timestamp': data.get('timestamp')
                    }, room=client)
        
        @self.socketio.on('ping')
        def handle_ping():
            # Responder al ping para verificar conectividad
            emit('pong', {
                'timestamp': data.get('timestamp'),
                'message': 'Servidor activo'
            })

    # Métodos públicos para notificaciones desde otras partes del sistema
    def notify_stock_update(self, product_id, new_stock, reason=""):
        """Método para notificar actualización de stock desde otros servicios"""
        self.handle_stock_update({
            'product_id': product_id,
            'new_stock': new_stock,
            'reason': reason,
            'timestamp': self._get_timestamp()
        })
    
    def notify_new_sale(self, sale_id, total, client_name="N/A"):
        """Método para notificar nueva venta desde otros servicios"""
        self.handle_new_sale({
            'sale_id': sale_id,
            'total': total,
            'client_name': client_name,
            'timestamp': self._get_timestamp()
        })
    
    def notify_new_product(self, product_id, product_name):
        """Método para notificar nuevo producto desde otros servicios"""
        self.handle_new_product({
            'product_id': product_id,
            'product_name': product_name,
            'timestamp': self._get_timestamp()
        })
    
    def notify_low_stock(self, product_id, product_name, current_stock, min_stock):
        """Método para notificar stock bajo desde otros servicios"""
        self.handle_low_stock_alert({
            'product_id': product_id,
            'product_name': product_name,
            'current_stock': current_stock,
            'min_stock': min_stock,
            'timestamp': self._get_timestamp()
        })
    
    def _get_timestamp(self):
        """Obtener timestamp actual"""
        from datetime import datetime
        return datetime.now().isoformat()

def initialize_sockets(socketio):
    """Función para inicializar el servidor de sockets"""
    notification_server = NotificationServer(socketio)
    print("[SOCKET] Servidor de notificaciones inicializado")
    return notification_server