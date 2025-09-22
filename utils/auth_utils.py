"""
Utilidades de Autenticación

Este módulo contiene funciones utilitarias para:
- Hash y verificación de contraseñas usando bcrypt
- Generación y validación de tokens JWT
- Funciones de seguridad auxiliares
"""
import bcrypt
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config.auth_config import auth_config

logging.basicConfig(level=logging.INFO)

class AuthUtils:
    """
    Clase con métodos estáticos para manejo de autenticación y seguridad.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera un hash seguro de la contraseña usando bcrypt.
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        try:
            # Convertir la contraseña a bytes
            password_bytes = password.encode('utf-8')
            
            # Generar salt y hash
            salt = bcrypt.gensalt(rounds=auth_config.BCRYPT_ROUNDS)
            hashed = bcrypt.hashpw(password_bytes, salt)
            
            # Retornar como string
            return hashed.decode('utf-8')
            
        except Exception as e:
            logging.error(f"Error al hashear contraseña: {e}")
            raise Exception("Error al procesar la contraseña")
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash.
        
        Args:
            password (str): Contraseña en texto plano
            hashed_password (str): Hash almacenado de la contraseña
            
        Returns:
            bool: True si la contraseña es correcta, False si no
        """
        try:
            # Convertir a bytes
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            
            # Verificar con bcrypt
            return bcrypt.checkpw(password_bytes, hashed_bytes)
            
        except Exception as e:
            logging.error(f"Error al verificar contraseña: {e}")
            return False
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token JWT de acceso.
        
        Args:
            data (dict): Datos a incluir en el token (user_id, username, role, etc.)
            expires_delta (timedelta, optional): Tiempo personalizado de expiración
            
        Returns:
            str: Token JWT firmado
        """
        try:
            # Hacer una copia de los datos para no modificar el original
            to_encode = data.copy()
            
            # Establecer tiempo de expiración
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + auth_config.get_token_expire_delta()
            
            # Agregar campos estándar del JWT
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access"
            })
            
            # Crear y firmar el token
            encoded_jwt = jwt.encode(
                to_encode, 
                auth_config.SECRET_KEY, 
                algorithm=auth_config.ALGORITHM
            )
            
            return encoded_jwt
            
        except Exception as e:
            logging.error(f"Error al crear token JWT: {e}")
            raise Exception("Error al generar token de acceso")
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica y decodifica un token JWT.
        
        Args:
            token (str): Token JWT a verificar
            
        Returns:
            dict: Datos decodificados del token, o None si es inválido
        """
        try:
            # Decodificar y verificar el token
            payload = jwt.decode(
                token,
                auth_config.SECRET_KEY,
                algorithms=[auth_config.ALGORITHM]
            )
            
            # Verificar que sea un token de acceso
            if payload.get("type") != "access":
                logging.warning("Token no es de tipo 'access'")
                return None
            
            # Verificar que no haya expirado (jwt.decode ya hace esto, pero por claridad)
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                logging.warning("Token ha expirado")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logging.warning("Token JWT ha expirado")
            return None
        except jwt.InvalidTokenError as e:
            logging.warning(f"Token JWT inválido: {e}")
            return None
        except Exception as e:
            logging.error(f"Error al verificar token JWT: {e}")
            return None
    
    @staticmethod
    def extract_token_from_header(authorization_header: str) -> Optional[str]:
        """
        Extrae el token JWT del header Authorization.
        
        Args:
            authorization_header (str): Header Authorization (ej: "Bearer token123")
            
        Returns:
            str: Token JWT extraído, o None si no es válido
        """
        try:
            if not authorization_header:
                return None
            
            # El header debe tener formato "Bearer <token>"
            parts = authorization_header.split()
            
            if len(parts) != 2 or parts[0].lower() != "bearer":
                logging.warning("Formato de Authorization header inválido")
                return None
            
            return parts[1]
            
        except Exception as e:
            logging.error(f"Error al extraer token del header: {e}")
            return None
    
    @staticmethod
    def create_user_token_data(user) -> Dict[str, Any]:
        """
        Crea el payload de datos para un token JWT basado en un usuario.
        
        Args:
            user: Objeto User del modelo
            
        Returns:
            dict: Datos para incluir en el token JWT
        """
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value if user.role else "user",
            "is_active": user.is_active
        }
    
    @staticmethod
    def is_token_valid_for_user(token_data: Dict[str, Any], user) -> bool:
        """
        Verifica si los datos del token corresponden al usuario actual.
        
        Args:
            token_data (dict): Datos decodificados del token
            user: Objeto User del modelo
            
        Returns:
            bool: True si el token es válido para el usuario
        """
        try:
            # Verificar que el user_id coincida
            if token_data.get("user_id") != user.user_id:
                return False
            
            # Verificar que el usuario siga activo
            if not user.is_active:
                return False
            
            # Verificar que el role no haya cambiado (opcional, para mayor seguridad)
            token_role = token_data.get("role")
            user_role = user.role.value if user.role else "user"
            if token_role != user_role:
                logging.warning(f"Role del usuario ha cambiado: token={token_role}, user={user_role}")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error al validar token para usuario: {e}")
            return False

# Funciones auxiliares para facilitar el uso
def hash_password(password: str) -> str:
    """Función auxiliar para hashear contraseñas"""
    return AuthUtils.hash_password(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Función auxiliar para verificar contraseñas"""
    return AuthUtils.verify_password(password, hashed_password)

def create_access_token(user) -> str:
    """Función auxiliar para crear tokens de acceso"""
    token_data = AuthUtils.create_user_token_data(user)
    return AuthUtils.create_access_token(token_data)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Función auxiliar para verificar tokens"""
    return AuthUtils.verify_token(token)