from flask import Flask, render_template, jsonify
from controllers.store_controller import store_bp  # Importamos el blueprint para las rutas de Store
from controllers.user_controller import user_bp   # Importamos el blueprint para las rutas de usuarios
from config.database import Base, engine, create_tables, initialize_data
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración de la aplicación
app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'  # Cambia esto en producción

def initialize_app():
    """
    Inicializar la aplicación: crear tablas, cargar datos iniciales, etc.
    """
    try:
        # Crear todas las tablas de la base de datos
        logger.info("Creando tablas de base de datos...")
        create_tables()
        logger.info("Tablas creadas exitosamente")
        
        # Inicializar datos
        logger.info("Inicializando datos...")
        initialize_data()
        logger.info("Datos inicializados exitosamente")
        
    except Exception as e:
        logger.error(f"Error al inicializar la aplicación: {e}")
        raise

# Ruta para la página de inicio (raíz)
@app.route('/')
def home():
    # Renderizar la plantilla index.html para la interfaz de usuario
    return render_template('index.html')  # Asegúrate de tener el archivo index.html en /templates

# Ruta de información de la API
@app.route('/api')
def api_info():
    """Información general de la API"""
    return jsonify({
        'name': 'Store API',
        'version': '1.0.0',
        'description': 'API para gestión de tiendas con autenticación',
        'endpoints': {
            'stores': '/api/stores',
            'users': '/api/users',
            'auth': {
                'register': '/api/users/register',
                'login': '/api/users/login',
                'profile': '/api/users/profile'
            }
        }
    })

# Ruta de estado de salud
@app.route('/health')
def health_check():
    """Endpoint para verificar el estado de la aplicación"""
    return jsonify({
        'status': 'healthy',
        'message': 'API funcionando correctamente'
    })

# Registrar los blueprints
app.register_blueprint(store_bp)  # Rutas de tiendas
app.register_blueprint(user_bp)   # Rutas de usuarios

# Manejo global de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Recurso no encontrado',
        'error': 'NOT_FOUND'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Error interno del servidor',
        'error': 'INTERNAL_ERROR'
    }), 500

if __name__ == "__main__":
    # Inicializar la aplicación
    initialize_app()
    
    logger.info("Iniciando servidor Flask...")
    logger.info("Endpoints disponibles:")
    logger.info("  - Página principal: http://localhost:5000/")
    logger.info("  - API info: http://localhost:5000/api")
    logger.info("  - Stores: http://localhost:5000/api/stores")
    logger.info("  - Users: http://localhost:5000/api/users")
    logger.info("  - Registro: http://localhost:5000/api/users/register")
    logger.info("  - Login: http://localhost:5000/api/users/login")
    
    # Ejecutar la aplicación con el modo debug activado
    app.run(debug=True, host='0.0.0.0', port=5000)
