"""
Decoradores de Autenticación

Este módulo contiene decoradores reutilizables para proteger endpoints:
- @token_required: Requiere token JWT válido
- @admin_required: Requiere permisos de administrador
"""
from functools import wraps
from flask import request, jsonify
import logging
from services.user_service import user_service
from utils.auth_utils import AuthUtils

logging.basicConfig(level=logging.INFO)

def token_required(f):
    """
    Decorador para requerir autenticación con token JWT.
    
    Uso:
    @token_required
    def mi_endpoint(current_user):
        # current_user contiene el objeto User autenticado
        pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = AuthUtils.extract_token_from_header(auth_header)
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token de acceso requerido',
                'error': 'MISSING_TOKEN'
            }), 401
        
        # Validar token y obtener usuario
        is_valid, message, current_user = user_service.validate_token_and_get_user(token)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message,
                'error': 'INVALID_TOKEN'
            }), 401
        
        # Pasar el usuario actual a la función
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """
    Decorador para requerir permisos de administrador.
    Debe usarse después de @token_required.
    
    Uso:
    @token_required
    @admin_required
    def mi_endpoint_admin(current_user):
        # Solo usuarios admin pueden acceder
        pass
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Se requieren permisos de administrador',
                'error': 'INSUFFICIENT_PERMISSIONS'
            }), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def optional_auth(f):
    """
    Decorador para autenticación opcional.
    Si hay token válido, pasa current_user, si no, pasa None.
    
    Uso:
    @optional_auth
    def mi_endpoint(current_user=None):
        if current_user:
            # Usuario autenticado
            pass
        else:
            # Usuario anónimo
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = None
        
        # Intentar obtener token del header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = AuthUtils.extract_token_from_header(auth_header)
            
            if token:
                # Intentar validar token
                is_valid, message, user = user_service.validate_token_and_get_user(token)
                if is_valid:
                    current_user = user
        
        # Pasar el usuario (puede ser None) a la función
        return f(current_user, *args, **kwargs)
    
    return decorated