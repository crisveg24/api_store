"""
Repositorio de Usuarios

Este módulo maneja todas las operaciones de base de datos relacionadas con usuarios:
- Operaciones CRUD (Create, Read, Update, Delete)
- Búsquedas por username, email, ID
- Gestión de estado de usuarios (activo/inactivo)
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
import logging
from models.user_model import User, UserRole
from config.database import get_session

logging.basicConfig(level=logging.INFO)

class UserRepository:
    """
    Repositorio para manejo de operaciones de usuarios en la base de datos.
    """
    
    def __init__(self):
        """Inicializar el repositorio"""
        pass
    
    def create_user(self, username: str, email: str, password_hash: str, 
                   role: UserRole = UserRole.USER) -> Optional[User]:
        """
        Crear un nuevo usuario en la base de datos.
        
        Args:
            username (str): Nombre de usuario único
            email (str): Email único del usuario
            password_hash (str): Hash de la contraseña
            role (UserRole): Rol del usuario (por defecto USER)
            
        Returns:
            User: Usuario creado, o None si hay error
        """
        session = None
        try:
            session = get_session()
            
            # Verificar que no exista username duplicado
            existing_username = session.query(User).filter(User.username == username).first()
            if existing_username:
                logging.warning(f"Username '{username}' ya existe")
                return None
            
            # Verificar que no exista email duplicado
            existing_email = session.query(User).filter(User.email == email).first()
            if existing_email:
                logging.warning(f"Email '{email}' ya existe")
                return None
            
            # Crear nuevo usuario
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                role=role,
                is_active=True
            )
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            logging.info(f"Usuario creado exitosamente: {username}")
            return new_user
            
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logging.error(f"Error de base de datos al crear usuario: {e}")
            return None
        except Exception as e:
            if session:
                session.rollback()
            logging.error(f"Error inesperado al crear usuario: {e}")
            return None
        finally:
            if session:
                session.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Buscar usuario por su ID.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            User: Usuario encontrado, o None si no existe
        """
        session = None
        try:
            session = get_session()
            user = session.query(User).filter(User.user_id == user_id).first()
            return user
            
        except SQLAlchemyError as e:
            logging.error(f"Error de base de datos al buscar usuario por ID: {e}")
            return None
        except Exception as e:
            logging.error(f"Error inesperado al buscar usuario por ID: {e}")
            return None
        finally:
            if session:
                session.close()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Buscar usuario por su username.
        
        Args:
            username (str): Nombre de usuario
            
        Returns:
            User: Usuario encontrado, o None si no existe
        """
        session = None
        try:
            session = get_session()
            user = session.query(User).filter(User.username == username).first()
            return user
            
        except SQLAlchemyError as e:
            logging.error(f"Error de base de datos al buscar usuario por username: {e}")
            return None
        except Exception as e:
            logging.error(f"Error inesperado al buscar usuario por username: {e}")
            return None
        finally:
            if session:
                session.close()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Buscar usuario por su email.
        
        Args:
            email (str): Email del usuario
            
        Returns:
            User: Usuario encontrado, o None si no existe
        """
        session = None
        try:
            session = get_session()
            user = session.query(User).filter(User.email == email).first()
            return user
            
        except SQLAlchemyError as e:
            logging.error(f"Error de base de datos al buscar usuario por email: {e}")
            return None
        except Exception as e:
            logging.error(f"Error inesperado al buscar usuario por email: {e}")
            return None
        finally:
            if session:
                session.close()
    
    def get_user_by_username_or_email(self, identifier: str) -> Optional[User]:
        """
        Buscar usuario por username o email (útil para login).
        
        Args:
            identifier (str): Username o email del usuario
            
        Returns:
            User: Usuario encontrado, o None si no existe
        """
        session = None
        try:
            session = get_session()
            user = session.query(User).filter(
                or_(User.username == identifier, User.email == identifier)
            ).first()
            return user
            
        except SQLAlchemyError as e:
            logging.error(f"Error de base de datos al buscar usuario por username/email: {e}")
            return None
        except Exception as e:
            logging.error(f"Error inesperado al buscar usuario por username/email: {e}")
            return None
        finally:
            if session:
                session.close()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Actualizar campos de un usuario.
        
        Args:
            user_id (int): ID del usuario a actualizar
            **kwargs: Campos a actualizar (email, password_hash, role, is_active, etc.)
            
        Returns:
            User: Usuario actualizado, o None si hay error
        """
        session = None
        try:
            session = get_session()
            
            # Buscar el usuario
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                logging.warning(f"Usuario con ID {user_id} no encontrado")
                return None
            
            # Actualizar campos permitidos
            allowed_fields = ['email', 'password_hash', 'role', 'is_active', 'last_login']
            updated_fields = []
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
                    updated_fields.append(field)
            
            if not updated_fields:
                logging.warning("No se proporcionaron campos válidos para actualizar")
                return user
            
            session.commit()
            session.refresh(user)
            
            logging.info(f"Usuario {user.username} actualizado: {updated_fields}")
            return user
            
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logging.error(f"Error de base de datos al actualizar usuario: {e}")
            return None
        except Exception as e:
            if session:
                session.rollback()
            logging.error(f"Error inesperado al actualizar usuario: {e}")
            return None
        finally:
            if session:
                session.close()
    
    def update_last_login(self, user_id: int) -> bool:
        """
        Actualizar la fecha de último login de un usuario.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            bool: True si se actualizó correctamente, False si hay error
        """
        session = None
        try:
            session = get_session()
            
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.update_last_login()
                session.commit()
                return True
            else:
                logging.warning(f"Usuario con ID {user_id} no encontrado para actualizar last_login")
                return False
            
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logging.error(f"Error de base de datos al actualizar last_login: {e}")
            return False
        except Exception as e:
            if session:
                session.rollback()
            logging.error(f"Error inesperado al actualizar last_login: {e}")
            return False
        finally:
            if session:
                session.close()
    
    def delete_user(self, user_id: int) -> bool:
        """
        Eliminar un usuario de la base de datos.
        
        Args:
            user_id (int): ID del usuario a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si hay error
        """
        session = None
        try:
            session = get_session()
            
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                logging.warning(f"Usuario con ID {user_id} no encontrado para eliminar")
                return False
            
            session.delete(user)
            session.commit()
            
            logging.info(f"Usuario {user.username} eliminado exitosamente")
            return True
            
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            logging.error(f"Error de base de datos al eliminar usuario: {e}")
            return False
        except Exception as e:
            if session:
                session.rollback()
            logging.error(f"Error inesperado al eliminar usuario: {e}")
            return False
        finally:
            if session:
                session.close()
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        Desactivar un usuario (establecer is_active = False).
        
        Args:
            user_id (int): ID del usuario a desactivar
            
        Returns:
            bool: True si se desactivó correctamente, False si hay error
        """
        return self.update_user(user_id, is_active=False) is not None
    
    def activate_user(self, user_id: int) -> bool:
        """
        Activar un usuario (establecer is_active = True).
        
        Args:
            user_id (int): ID del usuario a activar
            
        Returns:
            bool: True si se activó correctamente, False si hay error
        """
        return self.update_user(user_id, is_active=True) is not None
    
    def get_all_users(self, include_inactive: bool = False) -> List[User]:
        """
        Obtener todos los usuarios.
        
        Args:
            include_inactive (bool): Si incluir usuarios inactivos
            
        Returns:
            List[User]: Lista de usuarios
        """
        session = None
        try:
            session = get_session()
            
            query = session.query(User)
            if not include_inactive:
                query = query.filter(User.is_active == True)
            
            users = query.all()
            return users
            
        except SQLAlchemyError as e:
            logging.error(f"Error de base de datos al obtener usuarios: {e}")
            return []
        except Exception as e:
            logging.error(f"Error inesperado al obtener usuarios: {e}")
            return []
        finally:
            if session:
                session.close()
    
    def get_users_by_role(self, role: UserRole, include_inactive: bool = False) -> List[User]:
        """
        Obtener usuarios por rol.
        
        Args:
            role (UserRole): Rol a filtrar
            include_inactive (bool): Si incluir usuarios inactivos
            
        Returns:
            List[User]: Lista de usuarios con el rol especificado
        """
        session = None
        try:
            session = get_session()
            
            query = session.query(User).filter(User.role == role)
            if not include_inactive:
                query = query.filter(User.is_active == True)
            
            users = query.all()
            return users
            
        except SQLAlchemyError as e:
            logging.error(f"Error de base de datos al obtener usuarios por rol: {e}")
            return []
        except Exception as e:
            logging.error(f"Error inesperado al obtener usuarios por rol: {e}")
            return []
        finally:
            if session:
                session.close()
    
    def user_exists(self, username: str = None, email: str = None) -> bool:
        """
        Verificar si existe un usuario con el username o email especificado.
        
        Args:
            username (str, optional): Username a verificar
            email (str, optional): Email a verificar
            
        Returns:
            bool: True si el usuario existe, False si no
        """
        session = None
        try:
            session = get_session()
            
            if username and email:
                user = session.query(User).filter(
                    or_(User.username == username, User.email == email)
                ).first()
            elif username:
                user = session.query(User).filter(User.username == username).first()
            elif email:
                user = session.query(User).filter(User.email == email).first()
            else:
                return False
            
            return user is not None
            
        except SQLAlchemyError as e:
            logging.error(f"Error de base de datos al verificar existencia de usuario: {e}")
            return False
        except Exception as e:
            logging.error(f"Error inesperado al verificar existencia de usuario: {e}")
            return False
        finally:
            if session:
                session.close()

# Instancia global del repositorio
user_repository = UserRepository()