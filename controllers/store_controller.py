from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from services.store_service import StoreService
from services.user_service import user_service
from config.database import get_db_session
import logging

logging.basicConfig(level=logging.INFO)

store_bp = Blueprint('store_bp', __name__, url_prefix='/api')

# Instancia del servicio
service = StoreService(get_db_session())

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_current_user():
    """Helper para obtener el usuario actual desde el JWT"""
    user_id = get_jwt_identity()
    if user_id:
        return user_service.get_user_by_id(int(user_id))
    return None

def get_optional_current_user():
    """Helper para obtener el usuario actual de forma opcional"""
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            return user_service.get_user_by_id(int(user_id))
    except:
        pass
    return None

def check_admin_permissions(current_user):
    """Helper para verificar permisos de administrador"""
    if not current_user or not current_user.is_admin():
        return jsonify({
            'success': False,
            'message': 'Se requieren permisos de administrador',
            'error': 'INSUFFICIENT_PERMISSIONS'
        }), 403
    return None

def get_current_user():
    """Helper para obtener el usuario actual desde el JWT"""
    user_id = get_jwt_identity()
    if user_id:
        return user_service.get_user_by_id(int(user_id))
    return None

def get_optional_current_user():
    """Helper para obtener el usuario actual de forma opcional"""
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            return user_service.get_user_by_id(int(user_id))
    except:
        pass
    return None

def check_admin_permissions(current_user):
    """Helper para verificar permisos de administrador"""
    if not current_user or not current_user.is_admin():
        return jsonify({
            'success': False,
            'message': 'Se requieren permisos de administrador',
            'error': 'INSUFFICIENT_PERMISSIONS'
        }), 403
    return None

@store_bp.route('/stores', methods=['GET'])
def get_stores():
    """
    GET /stores
    Recupera y retorna tiendas con paginación.
    Endpoint público, pero muestra información adicional si el usuario está autenticado.
    
    Parámetros de consulta:
    - page: número de página (por defecto 1)
    - per_page: elementos por página (por defecto 10, máximo 100)
    """
    try:
        # Obtener usuario opcional
        current_user = get_optional_current_user()
        
        # Obtener parámetros de paginación desde la query string
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validar parámetros
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10
        if per_page > 100:  # Limitar el máximo de elementos por página
            per_page = 100
        
        # Obtener datos paginados
        result = service.listar_tiendas_paginadas(page, per_page)
        
        # Agregar información de autenticación si aplica
        if current_user:
            result['user_info'] = {
                'authenticated': True,
                'username': current_user.username,
                'role': current_user.role.value,
                'is_admin': current_user.is_admin()
            }
        else:
            result['user_info'] = {
                'authenticated': False
            }
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Error en get_stores: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

@store_bp.route('/stores', methods=['POST'])
@jwt_required()
def create_store():
    """
    POST /stores
    Crear una nueva tienda (solo administradores).
    
    Body JSON:
    {
        "store_area": float,
        "items_available": int,
        "daily_customer_count": int,
        "store_sales": float
    }
    """
    try:
        # Obtener usuario actual
        current_user = get_current_user()
        
        # Verificar permisos de administrador
        admin_check = check_admin_permissions(current_user)
        if admin_check:
            return admin_check
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos JSON requeridos',
                'error': 'MISSING_DATA'
            }), 400
        
        store_area = data.get('store_area')
        items_available = data.get('items_available')
        daily_customer_count = data.get('daily_customer_count')
        store_sales = data.get('store_sales')

        if not all([store_area is not None, items_available is not None, 
                   daily_customer_count is not None, store_sales is not None]):
            return jsonify({
                'success': False,
                'message': 'Todos los campos son obligatorios: store_area, items_available, daily_customer_count, store_sales',
                'error': 'MISSING_FIELDS'
            }), 400

        # Validar tipos de datos
        try:
            store_area = float(store_area)
            items_available = int(items_available)
            daily_customer_count = int(daily_customer_count)
            store_sales = float(store_sales)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Tipos de datos inválidos',
                'error': 'INVALID_DATA_TYPES'
            }), 400

        store = service.crear_tienda(store_area, items_available, daily_customer_count, store_sales)
        
        if store:
            logging.info(f"Tienda creada por usuario {current_user.username} (ID: {store.store_id})")
            return jsonify({
                'success': True,
                'message': 'Tienda creada exitosamente',
                'data': store.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Error al crear la tienda',
                'error': 'CREATION_FAILED'
            }), 500
            
    except Exception as e:
        logging.error(f"Error en create_store: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

@store_bp.route('/stores/<int:store_id>', methods=['GET'])
def get_store(store_id):
    """
    GET /stores/{store_id}
    Obtener una tienda específica.
    Endpoint público, pero muestra información adicional si el usuario está autenticado.
    """
    try:
        # Obtener usuario opcional
        current_user = get_optional_current_user()
        
        store = service.obtener_tienda(store_id)
        
        if store:
            store_data = store.to_dict()
            
            # Agregar información de autenticación si aplica
            if current_user:
                store_data['user_info'] = {
                    'authenticated': True,
                    'can_edit': current_user.is_admin(),
                    'username': current_user.username,
                    'role': current_user.role.value
                }
            else:
                store_data['user_info'] = {
                    'authenticated': False,
                    'can_edit': False
                }
            
            return jsonify({
                'success': True,
                'message': 'Tienda encontrada',
                'data': store_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Tienda no encontrada',
                'error': 'NOT_FOUND'
            }), 404
            
    except Exception as e:
        logging.error(f"Error en get_store: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

@store_bp.route('/stores/<int:store_id>', methods=['PUT'])
@jwt_required()
def update_store(store_id):
    """
    PUT /stores/{store_id}
    Actualizar una tienda existente (solo administradores).
    
    Body JSON:
    {
        "store_area": float (opcional),
        "items_available": int (opcional),
        "daily_customer_count": int (opcional),
        "store_sales": float (opcional)
    }
    """
    try:
        # Obtener usuario actual
        current_user = get_current_user()
        
        # Verificar permisos de administrador
        admin_check = check_admin_permissions(current_user)
        if admin_check:
            return admin_check
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos JSON requeridos',
                'error': 'MISSING_DATA'
            }), 400
        
        store_area = data.get('store_area')
        items_available = data.get('items_available')
        daily_customer_count = data.get('daily_customer_count')
        store_sales = data.get('store_sales')
        
        # Validar tipos de datos si se proporcionan
        try:
            if store_area is not None:
                store_area = float(store_area)
            if items_available is not None:
                items_available = int(items_available)
            if daily_customer_count is not None:
                daily_customer_count = int(daily_customer_count)
            if store_sales is not None:
                store_sales = float(store_sales)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Tipos de datos inválidos',
                'error': 'INVALID_DATA_TYPES'
            }), 400

        store = service.actualizar_tienda(store_id, store_area, items_available, daily_customer_count, store_sales)
        
        if store:
            logging.info(f"Tienda {store_id} actualizada por usuario {current_user.username}")
            return jsonify({
                'success': True,
                'message': 'Tienda actualizada exitosamente',
                'data': store.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Tienda no encontrada',
                'error': 'NOT_FOUND'
            }), 404
            
    except Exception as e:
        logging.error(f"Error en update_store: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

@store_bp.route('/stores/<int:store_id>', methods=['DELETE'])
@jwt_required()
def delete_store(store_id):
    """
    DELETE /stores/{store_id}
    Eliminar una tienda (solo administradores).
    """
    try:
        # Obtener usuario actual
        current_user = get_current_user()
        
        # Verificar permisos de administrador
        admin_check = check_admin_permissions(current_user)
        if admin_check:
            return admin_check
        
        success = service.eliminar_tienda(store_id)
        
        if success:
            logging.info(f"Tienda {store_id} eliminada por usuario {current_user.username}")
            return jsonify({
                'success': True,
                'message': 'Tienda eliminada exitosamente'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Tienda no encontrada',
                'error': 'NOT_FOUND'
            }), 404
            
    except Exception as e:
        logging.error(f"Error en delete_store: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

# ============================================================================
# ENDPOINT DE ESTADÍSTICAS (SOLO PARA ADMINISTRADORES)
# ============================================================================

@store_bp.route('/stores/stats', methods=['GET'])
@jwt_required()
def get_store_stats():
    """
    GET /stores/stats
    Obtener estadísticas de las tiendas (solo administradores).
    """
    try:
        # Obtener usuario actual
        current_user = get_current_user()
        
        # Verificar permisos de administrador
        admin_check = check_admin_permissions(current_user)
        if admin_check:
            return admin_check
        
        # Obtener estadísticas básicas del servicio
        stats = service.obtener_estadisticas()
        
        return jsonify({
            'success': True,
            'message': 'Estadísticas obtenidas exitosamente',
            'data': stats
        }), 200
        
    except Exception as e:
        logging.error(f"Error en get_store_stats: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

@store_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint no encontrado',
        'error': 'NOT_FOUND'
    }), 404

@store_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'message': 'Método HTTP no permitido',
        'error': 'METHOD_NOT_ALLOWED'
    }), 405
