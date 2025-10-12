from flask import Flask, render_template, jsonify
from flask_jwt_extended import JWTManager
from controllers.store_controller import store_bp  # Importamos el blueprint para las rutas de Store
from controllers.user_controller import user_bp   # Importamos el blueprint para las rutas de usuarios
from config.database import Base, engine, create_tables, initialize_data, init_app as init_db
from config.jwt_config import (
    JWT_SECRET_KEY, JWT_TOKEN_LOCATION, JWT_ACCESS_TOKEN_EXPIRES,
    JWT_HEADER_NAME, JWT_HEADER_TYPE, JWT_ERROR_MESSAGE_KEY
)
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config=None):
    """
    Factory function para crear la aplicación Flask.
    Permite configuración personalizada para testing.
    
    Args:
        config (dict, optional): Configuración personalizada para la app
        
    Returns:
        Flask: Aplicación Flask configurada
    """
    # Crear la aplicación Flask
    app = Flask(__name__)
    
    # Configuración de la aplicación
    app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'  # Cambia esto en producción
    
    # Configuración JWT
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    app.config['JWT_TOKEN_LOCATION'] = JWT_TOKEN_LOCATION
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
    app.config['JWT_HEADER_NAME'] = JWT_HEADER_NAME
    app.config['JWT_HEADER_TYPE'] = JWT_HEADER_TYPE
    app.config['JWT_ERROR_MESSAGE_KEY'] = JWT_ERROR_MESSAGE_KEY
    
    # Aplicar configuración personalizada si se proporciona
    if config:
        app.config.update(config)
    
    # Inicializar base de datos con la app
    init_db(app)
    
    # Inicializar JWT Manager
    jwt = JWTManager(app)
    
    # Configurar manejadores de errores JWT
    configure_jwt_handlers(jwt)
    
    # Ruta para la página de inicio (raíz)
    @app.route('/')
    def home():
        # Renderizar la plantilla index.html para la interfaz de usuario
        return render_template('index.html')
    
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
    
    return app

def configure_jwt_handlers(jwt):
    """
    Configurar manejadores de errores JWT.
    
    Args:
        jwt: Instancia de JWTManager
    """
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token ha expirado',
            'error': 'TOKEN_EXPIRED'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Token JWT inválido',
            'error': 'INVALID_TOKEN'
        }), 422
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Token de autorización requerido',
            'error': 'AUTHORIZATION_REQUIRED'
        }), 401


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

if __name__ == "__main__":
    # Crear la aplicación
    app = create_app()
    
    # Inicializar la aplicación (solo cuando se ejecuta directamente)
    with app.app_context():
        initialize_app()
    
    logger.info("Iniciando servidor Flask...")
    logger.info("Endpoints disponibles:")
    logger.info("  - Página principal: http://localhost:5000/")
    logger.info("  - API info: http://localhost:5000/api")
    logger.info("  - Stores: http://localhost:5000/api/stores")
    logger.info("  - Users: http://localhost:5000/api/users")
    logger.info("  - Registro: http://localhost:5000/api/users/register")
    logger.info("  - Login: http://localhost:5000/api/users/login")
    logger.info("  - Perfil: http://localhost:5000/api/users/profile")
    logger.info("  - Verificar Token: http://localhost:5000/api/users/verify-token")
    logger.info("  - Gestión Usuarios (Admin): http://localhost:5000/api/users/")
    logger.info("  - Cambiar Rol (Admin): PUT /api/users/{id}/role")
    logger.info("  - Activar/Desactivar (Admin): PUT /api/users/{id}/toggle-status")
    
    # Ejecutar la aplicación con el modo debug activado
    app.run(debug=True, host='0.0.0.0', port=5000)

