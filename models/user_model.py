"""
Modelo de Usuario

Este módulo define el modelo de datos para la tabla de usuarios usando SQLAlchemy.
Incluye funcionalidades para autenticación, autorización y gestión de usuarios.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

# Usamos la misma base que el modelo de Store
from models.store_model import Base

class UserRole(enum.Enum):
    """
    Enumeración para los roles de usuario.
    """
    ADMIN = "admin"      # Administrador: puede crear, leer, actualizar y eliminar
    USER = "user"        # Usuario: solo puede leer datos

class User(Base):
    """
    Modelo de usuario para el sistema de autenticación y autorización.
    
    Atributos:
        user_id (int): Identificador único del usuario (clave primaria)
        username (str): Nombre de usuario único para login
        email (str): Dirección de email única del usuario
        password_hash (str): Hash seguro de la contraseña usando bcrypt
        role (UserRole): Rol del usuario (admin o user)
        is_active (bool): Indica si el usuario está activo
        created_at (datetime): Fecha y hora de creación del usuario
        last_login (datetime): Última fecha y hora de login (opcional)
    """
    
    __tablename__ = 'users'
    
    # Campos de la tabla
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    def __init__(self, username, email, password_hash, role=UserRole.USER, is_active=True):
        """
        Constructor para crear un nuevo usuario.
        
        Args:
            username (str): Nombre de usuario
            email (str): Email del usuario  
            password_hash (str): Hash de la contraseña
            role (UserRole): Rol del usuario (por defecto USER)
            is_active (bool): Estado activo (por defecto True)
        """
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.created_at = datetime.utcnow()
    
    def to_dict(self, include_sensitive=False):
        """
        Convierte el objeto User a diccionario para serialización JSON.
        
        Args:
            include_sensitive (bool): Si incluir datos sensibles como password_hash
            
        Returns:
            dict: Representación del usuario en diccionario
        """
        user_dict = {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value if self.role else 'user',
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        # Solo incluir password_hash si se solicita explícitamente (para debugging)
        if include_sensitive:
            user_dict['password_hash'] = self.password_hash
            
        return user_dict
    
    def is_admin(self):
        """
        Verifica si el usuario tiene rol de administrador.
        
        Returns:
            bool: True si es administrador, False si no
        """
        return self.role == UserRole.ADMIN
    
    def update_last_login(self):
        """
        Actualiza la fecha y hora del último login.
        """
        self.last_login = datetime.utcnow()
    
    def __repr__(self):
        """
        Representación string del objeto User para debugging.
        
        Returns:
            str: Representación del usuario
        """
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}', role='{self.role.value if self.role else 'user'}', is_active={self.is_active})>"