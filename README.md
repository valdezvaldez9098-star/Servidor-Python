# Servidor POS en Python

Este es el repositorio del **servidor backend** para un sistema de punto de venta (POS), implementado en Python. Se encarga de manejar peticiones, procesar ventas, interactuar con base de datos, y servir como API para clientes (terminales POS).

---

## 📋 Contenido

- `main.py` — Punto de entrada del servidor.  
- `config.py` — Archivo de configuración con variables importantes (puerto, credenciales, etc.).  
- `requirements.txt` — Dependencias necesarias para correr el servidor.  
- `app/` — Carpeta con la lógica de la aplicación (rutas, controladores, modelos, utilidades, etc.).  

---

## 🚀 Características

- Servidor REST para operaciones POS (ventas, productos, usuarios, etc.).  
- Manejo de configuración por medio de `config.py`.  
- Modular: la carpeta `app` está preparada para organizar controladores, modelos y servicios.  
- Fácil de desplegar y extender.  

---

## 💻 Requisitos

- Python 3.8+  
- Paquetes listados en `requirements.txt`  
- (Opcional) Entorno virtual (recomendado)  

---

## 🛠️ Instalación

1. Clona este repositorio:

   ```bash
   git clone https://github.com/valdezvaldez9098-star/Servidor-Python.git
   cd Servidor-Python
