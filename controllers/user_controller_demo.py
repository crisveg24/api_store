"""
Controlador de Usuarios - Versión Simplificada para Demo JWT

Este módulo maneja los endpoints básicos de usuarios con Flask-JWT-Extended:
- Registro de usuarios
- Login (autenticación)
- Gestión de perfiles
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from services.user_service import user_service
from models.user_model import UserRole

logging.basicConfig(level=logging.INFO)

# Crear el blueprint para usuarios
user_bp = Blueprint('users', __name__, url_prefix='/api/users')

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_current_user():
    """Helper para obtener el usuario actual desde el JWT"""
    user_id = get_jwt_identity()
    if user_id:
        return user_service.get_user_by_id(int(user_id))
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

# ============================================================================
# ENDPOINTS PÚBLICOS (SIN AUTENTICACIÓN)
# ============================================================================

@user_bp.route('/register', methods=['POST'])
def register():
    """
    Registrar un nuevo usuario.
    
    Body JSON:
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos JSON requeridos',
                'error': 'MISSING_DATA'
            }), 400
        
        # Extraer datos
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validar campos requeridos
        if not all([username, email, password]):
            return jsonify({
                'success': False,
                'message': 'Username, email y password son requeridos',
                'error': 'MISSING_FIELDS'
            }), 400
        
        # Registrar usuario
        try:
            success, message, user_data = user_service.register_user(
                username=username.strip(),
                email=email.strip(),
                password=password,
                role=UserRole.USER  # Por defecto, usuarios normales
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'data': user_data
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'message': message,
                    'error': 'REGISTRATION_FAILED'
                }), 400
        except Exception as service_error:
            logging.error(f"Error en user_service.register_user: {service_error}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'message': f'Error en servicio: {str(service_error)}',
                'error': 'SERVICE_ERROR'
            }), 500
            
    except Exception as e:
        logging.error(f"Error en endpoint register: {e}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}',
            'error': 'INTERNAL_ERROR'
        }), 500

@user_bp.route('/login', methods=['POST'])
def login():
    """
    Autenticar usuario (login).
    
    Body JSON:
    {
        "identifier": "username o email",
        "password": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos JSON requeridos',
                'error': 'MISSING_DATA'
            }), 400
        
        # Extraer datos
        identifier = data.get('identifier')  # username o email
        password = data.get('password')
        
        # Validar campos requeridos
        if not all([identifier, password]):
            return jsonify({
                'success': False,
                'message': 'Identifier (username/email) y password son requeridos',
                'error': 'MISSING_FIELDS'
            }), 400
        
        # Intentar login
        success, message, user_data = user_service.login_user(
            identifier=identifier.strip(),
            password=password
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': user_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message,
                'error': 'LOGIN_FAILED'
            }), 401
            
    except Exception as e:
        logging.error(f"Error en endpoint login: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

# ============================================================================
# ENDPOINTS PROTEGIDOS (REQUIEREN AUTENTICACIÓN)
# ============================================================================

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Obtener el perfil del usuario autenticado.
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado',
                'error': 'USER_NOT_FOUND'
            }), 404
        
        success, message, user_data = user_service.get_user_profile(current_user.user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': user_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message,
                'error': 'PROFILE_ERROR'
            }), 404
            
    except Exception as e:
        logging.error(f"Error en endpoint get_profile: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

@user_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verificar que el token JWT es válido.
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Token válido pero usuario no encontrado',
                'error': 'USER_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Token válido',
            'data': {
                'user_id': current_user.user_id,
                'username': current_user.username,
                'email': current_user.email,
                'role': current_user.role.value,
                'is_active': current_user.is_active
            }
        }), 200
            
    except Exception as e:
        logging.error(f"Error en endpoint verify_token: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

# ============================================================================
# ENDPOINTS DE ADMINISTRACIÓN (SOLO PARA ADMINS)
# ============================================================================

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_users():
    """
    Obtener todos los usuarios registrados (solo administradores).
    
    Query params:
    - include_inactive: true/false (por defecto false)
    """
    try:
        current_user = get_current_user()
        admin_check = check_admin_permissions(current_user)
        if admin_check:
            return admin_check
        
        # Obtener parámetro opcional
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        success, message, users_data = user_service.get_all_users(
            requesting_user_id=current_user.user_id,
            include_inactive=include_inactive
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': users_data,
                'count': len(users_data) if users_data else 0
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message,
                'error': 'USERS_ERROR'
            }), 403
            
    except Exception as e:
        logging.error(f"Error en endpoint get_all_users: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

@user_bp.route('/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def change_user_role(user_id):
    """
    Cambiar el rol de un usuario (solo administradores).
    
    Body JSON:
    {
        "role": "admin" | "user"
    }
    """
    try:
        current_user = get_current_user()
        admin_check = check_admin_permissions(current_user)
        if admin_check:
            return admin_check
        
        data = request.get_json()
        if not data or 'role' not in data:
            return jsonify({
                'success': False,
                'message': 'El campo role es requerido',
                'error': 'MISSING_ROLE'
            }), 400
        
        new_role = data['role'].lower()
        if new_role not in ['admin', 'user']:
            return jsonify({
                'success': False,
                'message': 'El rol debe ser "admin" o "user"',
                'error': 'INVALID_ROLE'
            }), 400
        
        # Convertir string a enum
        role_enum = UserRole.ADMIN if new_role == 'admin' else UserRole.USER
        
        success, message, user_data = user_service.change_user_role(
            user_id=user_id,
            new_role=role_enum,
            admin_user_id=current_user.user_id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': user_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message,
                'error': 'ROLE_CHANGE_FAILED'
            }), 400
            
    except Exception as e:
        logging.error(f"Error en endpoint change_user_role: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

@user_bp.route('/<int:user_id>/toggle-status', methods=['PUT'])
@jwt_required()
def toggle_user_status(user_id):
    """
    Activar/desactivar un usuario (solo administradores).
    """
    try:
        current_user = get_current_user()
        admin_check = check_admin_permissions(current_user)
        if admin_check:
            return admin_check
        
        success, message, user_data = user_service.toggle_user_status(
            user_id=user_id,
            admin_user_id=current_user.user_id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': user_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message,
                'error': 'STATUS_TOGGLE_FAILED'
            }), 400
            
    except Exception as e:
        logging.error(f"Error en endpoint toggle_user_status: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500