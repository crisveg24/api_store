"""
Controlador de Usuarios

Este módulo maneja los endpoints relacionados con usuarios:
- Registro de usuarios
- Login (autenticación)
- Gestión de perfiles
- Administración de usuarios (solo admins)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
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
            
    except Exception as e:
        logging.error(f"Error en endpoint register: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
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

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Actualizar el perfil del usuario autenticado.
    
    Body JSON:
    {
        "email": "string (opcional)",
        "current_password": "string (requerido para cambiar contraseña)",
        "new_password": "string (opcional)"
    }
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado',
                'error': 'USER_NOT_FOUND'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos JSON requeridos',
                'error': 'MISSING_DATA'
            }), 400
        
        # Extraer datos opcionales
        email = data.get('email')
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Actualizar perfil
        success, message, user_data = user_service.update_user_profile(
            user_id=current_user.user_id,
            email=email.strip() if email else None,
            current_password=current_password,
            new_password=new_password
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
                'error': 'UPDATE_FAILED'
            }), 400
            
    except Exception as e:
        logging.error(f"Error en endpoint update_profile: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

# ============================================================================
# ENDPOINTS DE ADMINISTRACIÓN (SOLO ADMINS)
# ============================================================================

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_users():
    """
    Obtener todos los usuarios (solo administradores).
    
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

# ============================================================================
# ENDPOINTS DE ADMINISTRACIÓN (TEMPORALMENTE DESHABILITADOS - PENDIENTE ACTUALIZACIÓN)
# ============================================================================

# TODO: Actualizar estos endpoints para usar Flask-JWT-Extended

# @user_bp.route('/<int:user_id>', methods=['PUT'])
# @jwt_required()
# def update_user(user_id):

# ... resto de endpoints de admin comentados temporalmente ...
    """
    Actualizar información de un usuario (solo admins).
    
    Body JSON:
    {
        "username": "string (opcional)",
        "email": "string (opcional)",
        "password": "string (opcional)",
        "role": "user|admin (opcional)",
        "is_active": boolean (opcional)
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
        
        # Extraer datos opcionales
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        is_active = data.get('is_active')
        
        # Validaciones básicas
        if username is not None and (not username.strip() or len(username.strip()) < 3):
            return jsonify({
                'success': False,
                'message': 'Username debe tener al menos 3 caracteres',
                'error': 'INVALID_USERNAME'
            }), 400
            
        if email is not None and (not email.strip() or '@' not in email):
            return jsonify({
                'success': False,
                'message': 'Email válido requerido',
                'error': 'INVALID_EMAIL'
            }), 400
            
        if password is not None and len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password debe tener al menos 6 caracteres',
                'error': 'INVALID_PASSWORD'
            }), 400
            
        if role is not None and role not in ['user', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Role debe ser "user" o "admin"',
                'error': 'INVALID_ROLE'
            }), 400
        
        # Convertir role string a enum si se proporciona
        user_role = None
        if role:
            user_role = UserRole.ADMIN if role == 'admin' else UserRole.USER
        
        # Actualizar usuario
        success, message, user_data = user_service.update_user_by_admin(
            admin_user_id=current_user.user_id,
            target_user_id=user_id,
            username=username.strip() if username else None,
            email=email.strip() if email else None,
            password=password,
            role=user_role,
            is_active=is_active
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
                'error': 'UPDATE_FAILED'
            }), 400
            
    except Exception as e:
        logging.error(f"Error en endpoint update_user: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

@user_bp.route('/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    """
    Actualizar el rol de un usuario (solo admins).
    
    Body JSON:
    {
        "role": "admin" | "user"
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
        
        role_str = data.get('role')
        if not role_str:
            return jsonify({
                'success': False,
                'message': 'Role es requerido',
                'error': 'MISSING_ROLE'
            }), 400
        
        # Convertir string a UserRole
        try:
            new_role = UserRole.ADMIN if role_str.lower() == 'admin' else UserRole.USER
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Role inválido. Debe ser "admin" o "user"',
                'error': 'INVALID_ROLE'
            }), 400
        
        # Actualizar rol
        success, message, user_data = user_service.update_user_role(
            admin_user_id=current_user.user_id,
            target_user_id=user_id,
            new_role=new_role
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
                'error': 'ROLE_UPDATE_FAILED'
            }), 400
            
    except Exception as e:
        logging.error(f"Error en endpoint update_user_role: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

@user_bp.route('/<int:user_id>/toggle-status', methods=['PUT'])
@jwt_required()
def toggle_user_status(user_id):
    """
    Activar/desactivar un usuario (solo admins).
    """
    try:
        # Obtener usuario actual
        current_user = get_current_user()
        
        # Verificar permisos de administrador
        admin_check = check_admin_permissions(current_user)
        if admin_check:
            return admin_check
        
        success, message, user_data = user_service.toggle_user_status(
            admin_user_id=current_user.user_id,
            target_user_id=user_id
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
                'error': 'STATUS_UPDATE_FAILED'
            }), 400
            
    except Exception as e:
        logging.error(f"Error en endpoint toggle_user_status: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Eliminar un usuario (solo admins).
    """
    try:
        # Obtener usuario actual
        current_user = get_current_user()
        
        # Verificar permisos de administrador
        admin_check = check_admin_permissions(current_user)
        if admin_check:
            return admin_check
        
        success, message = user_service.delete_user(
            admin_user_id=current_user.user_id,
            target_user_id=user_id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message,
                'error': 'DELETE_FAILED'
            }), 400
            
    except Exception as e:
        logging.error(f"Error en endpoint delete_user: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

@user_bp.route('/create-admin', methods=['POST'])
def create_admin():
    """
    Crear un usuario administrador por defecto.
    Solo funciona si no existe ningún admin.
    
    Body JSON (opcional):
    {
        "username": "string",
        "email": "string", 
        "password": "string"
    }
    """
    try:
        data = request.get_json() or {}
        
        # Usar valores por defecto si no se proporcionan
        username = data.get('username', 'admin')
        email = data.get('email', 'admin@tienda.com')
        password = data.get('password', 'Admin123!')
        
        # Crear admin
        success, message, user_data = user_service.create_admin_user(
            username=username,
            email=email,
            password=password
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
                'error': 'ADMIN_CREATION_FAILED'
            }), 400
            
    except Exception as e:
        logging.error(f"Error en endpoint create_admin: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

# ============================================================================
# ENDPOINT DE VERIFICACIÓN DE TOKEN
# ============================================================================

@user_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verificar si un token es válido y obtener información del usuario.
    """
    try:
        # Obtener usuario actual
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado',
                'error': 'USER_NOT_FOUND'
            }), 404
        
        user_data = {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role.value,
            "is_active": current_user.is_active
        }
        
        return jsonify({
            'success': True,
            'message': 'Token válido',
            'data': user_data
        }), 200
        
    except Exception as e:
        logging.error(f"Error en endpoint verify_token: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

# ============================================================================
# ENDPOINT PARA CREAR USUARIOS (SOLO ADMINS)
# ============================================================================

@user_bp.route('/create', methods=['POST'])
@jwt_required()
def create_user():
    """
    Endpoint para que los administradores creen nuevos usuarios.
    
    Body JSON:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "role": "user|admin" (opcional, por defecto "user")
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
        
        # Validar datos requeridos
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos JSON requeridos',
                'error': 'MISSING_DATA'
            }), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', 'user').strip().lower()
        
        # Validaciones
        if not username or len(username) < 3:
            return jsonify({
                'success': False,
                'message': 'Username debe tener al menos 3 caracteres',
                'error': 'INVALID_USERNAME'
            }), 400
            
        if not email or '@' not in email:
            return jsonify({
                'success': False,
                'message': 'Email válido requerido',
                'error': 'INVALID_EMAIL'
            }), 400
            
        if not password or len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password debe tener al menos 6 caracteres',
                'error': 'INVALID_PASSWORD'
            }), 400
            
        if role not in ['user', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Role debe ser "user" o "admin"',
                'error': 'INVALID_ROLE'
            }), 400
        
        # Convertir role string a enum
        user_role = UserRole.ADMIN if role == 'admin' else UserRole.USER
        
        # Crear usuario
        success, message, user_data = user_service.register_user(
            username=username,
            email=email,
            password=password,
            role=user_role
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Usuario {role} creado exitosamente',
                'data': user_data
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message,
                'error': 'USER_CREATION_FAILED'
            }), 400
            
    except Exception as e:
        logging.error(f"Error en endpoint create_user: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': 'INTERNAL_ERROR'
        }), 500

# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

@user_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint no encontrado',
        'error': 'NOT_FOUND'
    }), 404

@user_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'message': 'Método HTTP no permitido',
        'error': 'METHOD_NOT_ALLOWED'
    }), 405

@user_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Error interno del servidor',
        'error': 'INTERNAL_ERROR'
    }), 500