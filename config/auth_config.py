"""
Configuración de Autenticación y Seguridad

Este módulo contiene todas las configuraciones relacionadas con la seguridad,
autenticación JWT y hash de contraseñas.
"""
import os
import secrets
from datetime import timedelta

class AuthConfig:
    """
    Configuración central para autenticación y seguridad.
    """
    
    # Clave secreta para firmar JWT tokens
    # En producción, esto debe ser una variable de entorno muy segura
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))
    
    # Algoritmo para firmar JWT tokens
    ALGORITHM = "HS256"
    
    # Tiempo de expiración para JWT tokens
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutos por defecto
    
    # Tiempo de expiración para tokens de refresh (para futuras implementaciones)
    REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 días
    
    # Configuración de bcrypt para hash de contraseñas
    BCRYPT_ROUNDS = 12  # Número de rondas para el hash (más rondas = más seguro pero más lento)
    
    # Configuraciones de validación de contraseñas
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True  
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Lista de caracteres especiales permitidos/requeridos
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Configuraciones de usuario
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    
    # Configuraciones de sesión
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    @classmethod
    def get_token_expire_delta(cls):
        """
        Retorna el timedelta para expiración de tokens.
        
        Returns:
            timedelta: Tiempo de expiración para tokens JWT
        """
        return timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    @classmethod
    def get_refresh_token_expire_delta(cls):
        """
        Retorna el timedelta para expiración de refresh tokens.
        
        Returns:
            timedelta: Tiempo de expiración para refresh tokens
        """
        return timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
    
    @classmethod
    def validate_password_strength(cls, password):
        """
        Valida la fortaleza de una contraseña según las políticas configuradas.
        
        Args:
            password (str): Contraseña a validar
            
        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        errors = []
        
        # Validar longitud mínima
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            errors.append(f"La contraseña debe tener al menos {cls.MIN_PASSWORD_LENGTH} caracteres")
        
        # Validar mayúsculas
        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("La contraseña debe contener al menos una letra mayúscula")
        
        # Validar minúsculas
        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("La contraseña debe contener al menos una letra minúscula")
        
        # Validar números
        if cls.REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            errors.append("La contraseña debe contener al menos un número")
        
        # Validar caracteres especiales
        if cls.REQUIRE_SPECIAL_CHARS and not any(c in cls.SPECIAL_CHARS for c in password):
            errors.append(f"La contraseña debe contener al menos uno de estos caracteres especiales: {cls.SPECIAL_CHARS}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_username(cls, username):
        """
        Valida el formato de un nombre de usuario.
        
        Args:
            username (str): Nombre de usuario a validar
            
        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        errors = []
        
        # Validar longitud
        if len(username) < cls.MIN_USERNAME_LENGTH:
            errors.append(f"El nombre de usuario debe tener al menos {cls.MIN_USERNAME_LENGTH} caracteres")
        
        if len(username) > cls.MAX_USERNAME_LENGTH:
            errors.append(f"El nombre de usuario no puede tener más de {cls.MAX_USERNAME_LENGTH} caracteres")
        
        # Validar caracteres permitidos (solo letras, números y guiones bajos)
        if not username.replace('_', '').replace('-', '').isalnum():
            errors.append("El nombre de usuario solo puede contener letras, números, guiones (-) y guiones bajos (_)")
        
        # No puede empezar con número
        if username[0].isdigit():
            errors.append("El nombre de usuario no puede empezar con un número")
        
        return len(errors) == 0, errors

# Configuraciones específicas para desarrollo y producción
class DevelopmentConfig(AuthConfig):
    """Configuración para desarrollo - menos segura pero más conveniente"""
    ACCESS_TOKEN_EXPIRE_MINUTES = 120  # 2 horas para desarrollo
    BCRYPT_ROUNDS = 4  # Menos rondas para ser más rápido en desarrollo

class ProductionConfig(AuthConfig):
    """Configuración para producción - máxima seguridad"""
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutos en producción
    BCRYPT_ROUNDS = 14  # Más rondas para máxima seguridad
    REQUIRE_SPECIAL_CHARS = True

# Seleccionar configuración basada en el entorno
ENVIRONMENT = os.getenv('FLASK_ENV', 'development')

if ENVIRONMENT == 'production':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()

# Exportar la configuración seleccionada
auth_config = config