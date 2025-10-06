"""
Servicio de Usuarios

Este módulo contiene la lógica de negocio para la gestión de usuarios:
- Registro de nuevos usuarios
- Autenticación (login)
- Validación de credenciales
- Gestión de roles y permisos
- Operaciones de administración de usuarios
"""
from typing import Optional, Dict, Any, List, Tuple
import logging
from datetime import datetime
from flask_jwt_extended import create_access_token
from repositories.user_repository import user_repository
from models.user_model import User, UserRole
from utils.auth_utils import hash_password, verify_password
from config.auth_config import auth_config

logging.basicConfig(level=logging.INFO)

class UserService:
    """
    Servicio para manejar la lógica de negocio de usuarios.
    """
    
    def __init__(self):
        """Inicializar el servicio de usuarios"""
        self.user_repository = user_repository
    
    def register_user(self, username: str, email: str, password: str, 
                     role: UserRole = UserRole.USER) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Registrar un nuevo usuario.
        
        Args:
            username (str): Nombre de usuario
            email (str): Email del usuario
            password (str): Contraseña en texto plano
            role (UserRole): Rol del usuario (por defecto USER)
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (éxito, mensaje, datos_usuario)
        """
        try:
            # Validar datos de entrada
            validation_result = self._validate_registration_data(username, email, password)
            if not validation_result[0]:
                return False, validation_result[1], None
            
            # Verificar que no exista el usuario
            if self.user_repository.user_exists(username=username, email=email):
                return False, "El usuario o email ya existe", None
            
            # Hashear la contraseña
            password_hash = hash_password(password)
            
            # Crear el usuario
            new_user = self.user_repository.create_user(
                username=username,
                email=email,
                password_hash=password_hash,
                role=role
            )
            
            if new_user:
                user_data = {
                    "user_id": new_user.user_id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "role": new_user.role.value,
                    "is_active": new_user.is_active,
                    "created_at": new_user.created_at.isoformat() if new_user.created_at else None
                }
                
                logging.info(f"Usuario registrado exitosamente: {username}")
                return True, "Usuario registrado exitosamente", user_data
            else:
                return False, "Error al crear el usuario", None
                
        except Exception as e:
            logging.error(f"Error en registro de usuario: {e}")
            return False, "Error interno del servidor", None
    
    def login_user(self, identifier: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Autenticar un usuario (login).
        
        Args:
            identifier (str): Username o email del usuario
            password (str): Contraseña en texto plano
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (éxito, mensaje, datos_con_token)
        """
        try:
            # Validar datos de entrada
            if not identifier or not password:
                return False, "Username/email y contraseña son requeridos", None
            
            # Buscar el usuario
            user = self.user_repository.get_user_by_username_or_email(identifier)
            if not user:
                return False, "Credenciales inválidas", None
            
            # Verificar que el usuario esté activo
            if not user.is_active:
                return False, "Cuenta desactivada", None
            
            # Verificar la contraseña
            if not verify_password(password, user.password_hash):
                return False, "Credenciales inválidas", None
            
            # Actualizar último login
            self.user_repository.update_last_login(user.user_id)
            
            # Crear token JWT usando Flask-JWT-Extended
            token = create_access_token(identity=str(user.user_id))
            
            # Preparar datos de respuesta
            user_data = {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "access_token": token,
                "token_type": "bearer"
            }
            
            logging.info(f"Login exitoso para usuario: {user.username}")
            return True, "Login exitoso", user_data
            
        except Exception as e:
            logging.error(f"Error en login de usuario: {e}")
            return False, "Error interno del servidor", None
    
    def get_user_profile(self, user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Obtener el perfil de un usuario.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (éxito, mensaje, datos_usuario)
        """
        try:
            user = self.user_repository.get_user_by_id(user_id)
            if not user:
                return False, "Usuario no encontrado", None
            
            user_data = {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            
            return True, "Perfil obtenido exitosamente", user_data
            
        except Exception as e:
            logging.error(f"Error al obtener perfil de usuario: {e}")
            return False, "Error interno del servidor", None
    
    def update_user_profile(self, user_id: int, email: str = None, 
                           current_password: str = None, new_password: str = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Actualizar el perfil de un usuario.
        
        Args:
            user_id (int): ID del usuario
            email (str, optional): Nuevo email
            current_password (str, optional): Contraseña actual (requerida para cambiar contraseña)
            new_password (str, optional): Nueva contraseña
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (éxito, mensaje, datos_usuario)
        """
        try:
            # Buscar el usuario
            user = self.user_repository.get_user_by_id(user_id)
            if not user:
                return False, "Usuario no encontrado", None
            
            update_data = {}
            
            # Actualizar email si se proporciona
            if email and email != user.email:
                # Validar email
                if not auth_config.is_valid_email(email):
                    return False, "Email inválido", None
                
                # Verificar que el email no esté en uso
                if self.user_repository.get_user_by_email(email):
                    return False, "El email ya está en uso", None
                
                update_data['email'] = email
            
            # Actualizar contraseña si se proporciona
            if new_password:
                if not current_password:
                    return False, "Contraseña actual requerida para cambiar contraseña", None
                
                # Verificar contraseña actual
                if not verify_password(current_password, user.password_hash):
                    return False, "Contraseña actual incorrecta", None
                
                # Validar nueva contraseña
                password_validation = auth_config.validate_password(new_password)
                if not password_validation['is_valid']:
                    return False, f"Contraseña inválida: {', '.join(password_validation['errors'])}", None
                
                # Hashear nueva contraseña
                update_data['password_hash'] = hash_password(new_password)
            
            # Actualizar usuario si hay cambios
            if update_data:
                updated_user = self.user_repository.update_user(user_id, **update_data)
                if updated_user:
                    user_data = {
                        "user_id": updated_user.user_id,
                        "username": updated_user.username,
                        "email": updated_user.email,
                        "role": updated_user.role.value,
                        "is_active": updated_user.is_active
                    }
                    return True, "Perfil actualizado exitosamente", user_data
                else:
                    return False, "Error al actualizar perfil", None
            else:
                return True, "No hay cambios para actualizar", None
                
        except Exception as e:
            logging.error(f"Error al actualizar perfil de usuario: {e}")
            return False, "Error interno del servidor", None
    
    def get_all_users(self, requesting_user_id: int, include_inactive: bool = False) -> Tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        """
        Obtener todos los usuarios (solo para administradores).
        
        Args:
            requesting_user_id (int): ID del usuario que solicita la información
            include_inactive (bool): Si incluir usuarios inactivos
            
        Returns:
            Tuple[bool, str, Optional[List[Dict]]]: (éxito, mensaje, lista_usuarios)
        """
        try:
            # Verificar que el usuario solicitante sea admin
            requesting_user = self.user_repository.get_user_by_id(requesting_user_id)
            if not requesting_user or not requesting_user.is_admin():
                return False, "Acceso denegado: se requieren permisos de administrador", None
            
            # Obtener todos los usuarios
            users = self.user_repository.get_all_users(include_inactive=include_inactive)
            
            users_data = []
            for user in users:
                user_data = {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                users_data.append(user_data)
            
            return True, "Usuarios obtenidos exitosamente", users_data
            
        except Exception as e:
            logging.error(f"Error al obtener todos los usuarios: {e}")
            return False, "Error interno del servidor", None
    
    def update_user_role(self, admin_user_id: int, target_user_id: int, new_role: UserRole) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Actualizar el rol de un usuario (solo para administradores).
        
        Args:
            admin_user_id (int): ID del administrador
            target_user_id (int): ID del usuario a actualizar
            new_role (UserRole): Nuevo rol
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (éxito, mensaje, datos_usuario)
        """
        try:
            # Verificar que el usuario solicitante sea admin
            admin_user = self.user_repository.get_user_by_id(admin_user_id)
            if not admin_user or not admin_user.is_admin():
                return False, "Acceso denegado: se requieren permisos de administrador", None
            
            # Verificar que no se esté modificando a sí mismo
            if admin_user_id == target_user_id:
                return False, "No puedes modificar tu propio rol", None
            
            # Actualizar el rol
            updated_user = self.user_repository.update_user(target_user_id, role=new_role)
            if updated_user:
                user_data = {
                    "user_id": updated_user.user_id,
                    "username": updated_user.username,
                    "email": updated_user.email,
                    "role": updated_user.role.value,
                    "is_active": updated_user.is_active
                }
                
                logging.info(f"Rol de usuario {updated_user.username} actualizado a {new_role.value} por {admin_user.username}")
                return True, "Rol actualizado exitosamente", user_data
            else:
                return False, "Usuario no encontrado", None
                
        except Exception as e:
            logging.error(f"Error al actualizar rol de usuario: {e}")
            return False, "Error interno del servidor", None
    
    def toggle_user_status(self, admin_user_id: int, target_user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Activar/desactivar un usuario (solo para administradores).
        
        Args:
            admin_user_id (int): ID del administrador
            target_user_id (int): ID del usuario a modificar
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (éxito, mensaje, datos_usuario)
        """
        try:
            # Verificar que el usuario solicitante sea admin
            admin_user = self.user_repository.get_user_by_id(admin_user_id)
            if not admin_user or not admin_user.is_admin():
                return False, "Acceso denegado: se requieren permisos de administrador", None
            
            # Verificar que no se esté modificando a sí mismo
            if admin_user_id == target_user_id:
                return False, "No puedes modificar tu propio estado", None
            
            # Obtener usuario objetivo
            target_user = self.user_repository.get_user_by_id(target_user_id)
            if not target_user:
                return False, "Usuario no encontrado", None
            
            # Cambiar estado
            new_status = not target_user.is_active
            updated_user = self.user_repository.update_user(target_user_id, is_active=new_status)
            
            if updated_user:
                user_data = {
                    "user_id": updated_user.user_id,
                    "username": updated_user.username,
                    "email": updated_user.email,
                    "role": updated_user.role.value,
                    "is_active": updated_user.is_active
                }
                
                status_text = "activado" if new_status else "desactivado"
                logging.info(f"Usuario {updated_user.username} {status_text} por {admin_user.username}")
                return True, f"Usuario {status_text} exitosamente", user_data
            else:
                return False, "Error al actualizar estado del usuario", None
                
        except Exception as e:
            logging.error(f"Error al cambiar estado de usuario: {e}")
            return False, "Error interno del servidor", None
    
    def delete_user(self, admin_user_id: int, target_user_id: int) -> Tuple[bool, str]:
        """
        Eliminar un usuario (solo para administradores).
        
        Args:
            admin_user_id (int): ID del administrador
            target_user_id (int): ID del usuario a eliminar
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Verificar que el usuario solicitante sea admin
            admin_user = self.user_repository.get_user_by_id(admin_user_id)
            if not admin_user or not admin_user.is_admin():
                return False, "Acceso denegado: se requieren permisos de administrador"
            
            # Verificar que no se esté eliminando a sí mismo
            if admin_user_id == target_user_id:
                return False, "No puedes eliminar tu propia cuenta"
            
            # Obtener el usuario para logging
            target_user = self.user_repository.get_user_by_id(target_user_id)
            if not target_user:
                return False, "Usuario no encontrado"
            
            # Eliminar usuario
            if self.user_repository.delete_user(target_user_id):
                logging.info(f"Usuario {target_user.username} eliminado por {admin_user.username}")
                return True, "Usuario eliminado exitosamente"
            else:
                return False, "Error al eliminar usuario"
                
        except Exception as e:
            logging.error(f"Error al eliminar usuario: {e}")
            return False, "Error interno del servidor"
    
    def validate_token_and_get_user(self, token: str) -> Tuple[bool, str, Optional[User]]:
        """
        Validar un token JWT y obtener el usuario correspondiente.
        
        Args:
            token (str): Token JWT
            
        Returns:
            Tuple[bool, str, Optional[User]]: (válido, mensaje, usuario)
        """
        try:
            # Verificar el token
            token_data = self.auth_utils.verify_token(token)
            if not token_data:
                return False, "Token inválido o expirado", None
            
            # Obtener el usuario
            user_id = token_data.get('user_id')
            if not user_id:
                return False, "Token inválido: falta user_id", None
            
            user = self.user_repository.get_user_by_id(user_id)
            if not user:
                return False, "Usuario no encontrado", None
            
            # Verificar que el token sea válido para este usuario
            if not self.auth_utils.is_token_valid_for_user(token_data, user):
                return False, "Token inválido para este usuario", None
            
            return True, "Token válido", user
            
        except Exception as e:
            logging.error(f"Error al validar token: {e}")
            return False, "Error interno del servidor", None
    
    def create_admin_user(self, username: str = "admin", email: str = "admin@tienda.com", 
                         password: str = "Admin123!") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Crear un usuario administrador por defecto.
        
        Args:
            username (str): Username del admin (por defecto "admin")
            email (str): Email del admin
            password (str): Contraseña del admin
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (éxito, mensaje, datos_usuario)
        """
        try:
            # Verificar si ya existe un admin
            admin_users = self.user_repository.get_users_by_role(UserRole.ADMIN)
            if admin_users:
                return False, "Ya existe al menos un usuario administrador", None
            
            # Crear usuario admin
            return self.register_user(username, email, password, UserRole.ADMIN)
            
        except Exception as e:
            logging.error(f"Error al crear usuario admin: {e}")
            return False, "Error interno del servidor", None
    
    def update_user_by_admin(self, admin_user_id: int, target_user_id: int, 
                           username: str = None, email: str = None, password: str = None,
                           role: UserRole = None, is_active: bool = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Actualizar información completa de un usuario (solo admins).
        
        Args:
            admin_user_id (int): ID del admin que realiza la operación
            target_user_id (int): ID del usuario a actualizar
            username (str, optional): Nuevo username
            email (str, optional): Nuevo email
            password (str, optional): Nueva contraseña
            role (UserRole, optional): Nuevo rol
            is_active (bool, optional): Nuevo estado activo
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (éxito, mensaje, datos_usuario)
        """
        try:
            # Verificar que el admin existe y tiene permisos
            admin_user = self.user_repository.get_user_by_id(admin_user_id)
            if not admin_user or not admin_user.is_admin():
                return False, "No tienes permisos para realizar esta acción", None
            
            # Verificar que el usuario objetivo existe
            target_user = self.user_repository.get_user_by_id(target_user_id)
            if not target_user:
                return False, "Usuario no encontrado", None
            
            # Prevenir que el admin se desactive a sí mismo
            if target_user_id == admin_user_id and is_active is False:
                return False, "No puedes desactivar tu propia cuenta", None
            
            # Verificar unicidad de username si se está cambiando
            if username and username != target_user.username:
                existing_user = self.user_repository.get_user_by_username(username)
                if existing_user:
                    return False, "El username ya está en uso", None
            
            # Verificar unicidad de email si se está cambiando
            if email and email != target_user.email:
                existing_user = self.user_repository.get_user_by_email(email)
                if existing_user:
                    return False, "El email ya está en uso", None
            
            # Preparar datos para actualizar
            update_data = {}
            
            if username:
                update_data['username'] = username
            
            if email:
                update_data['email'] = email
            
            if password:
                update_data['password_hash'] = hash_password(password)
            
            if role is not None:
                update_data['role'] = role
            
            if is_active is not None:
                update_data['is_active'] = is_active
            
            # Actualizar usuario
            updated_user = self.user_repository.update_user(target_user_id, **update_data)
            
            if updated_user:
                # Preparar datos de respuesta
                user_data = {
                    "user_id": updated_user.user_id,
                    "username": updated_user.username,
                    "email": updated_user.email,
                    "role": updated_user.role.value,
                    "is_active": updated_user.is_active,
                    "created_at": updated_user.created_at.isoformat() if updated_user.created_at else None,
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                logging.info(f"Usuario {target_user_id} actualizado por admin {admin_user_id}")
                return True, "Usuario actualizado exitosamente", user_data
            else:
                return False, "Error al actualizar usuario", None
                
        except Exception as e:
            logging.error(f"Error al actualizar usuario por admin: {e}")
            return False, "Error interno del servidor", None

    def _validate_registration_data(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """
        Validar datos de registro de usuario.
        
        Args:
            username (str): Nombre de usuario
            email (str): Email
            password (str): Contraseña
            
        Returns:
            Tuple[bool, str]: (válido, mensaje)
        """
        # Validar username
        username_validation = auth_config.validate_username(username)
        if not username_validation['is_valid']:
            return False, f"Username inválido: {', '.join(username_validation['errors'])}"
        
        # Validar email
        if not auth_config.is_valid_email(email):
            return False, "Email inválido"
        
        # Validar contraseña
        password_validation = auth_config.validate_password_strength(password)
        if not password_validation['is_valid']:
            return False, f"Contraseña inválida: {', '.join(password_validation['errors'])}"
        
        return True, "Datos válidos"
    
    def get_all_users(self, requesting_user_id: int, include_inactive: bool = False) -> Tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        """
        Obtener todos los usuarios (solo para administradores).
        
        Args:
            requesting_user_id (int): ID del usuario que hace la petición
            include_inactive (bool): Si incluir usuarios inactivos
            
        Returns:
            Tuple[bool, str, Optional[List[Dict]]]: (éxito, mensaje, lista_usuarios)
        """
        try:
            # Verificar que el usuario que hace la petición sea admin
            requesting_user = self.user_repository.get_user_by_id(requesting_user_id)
            if not requesting_user or not requesting_user.is_admin():
                return False, "Se requieren permisos de administrador", None
            
            users = self.user_repository.get_all_users(include_inactive=include_inactive)
            
            users_data = []
            for user in users:
                user_data = {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                users_data.append(user_data)
            
            return True, f"Se encontraron {len(users_data)} usuarios", users_data
            
        except Exception as e:
            logging.error(f"Error al obtener usuarios: {e}")
            return False, "Error interno del servidor", None
    
    def change_user_role(self, user_id: int, new_role: UserRole, admin_user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Cambiar el rol de un usuario (solo para administradores).
        
        Args:
            user_id (int): ID del usuario a modificar
            new_role (UserRole): Nuevo rol
            admin_user_id (int): ID del administrador que hace el cambio
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (éxito, mensaje, datos_usuario)
        """
        try:
            # Verificar que el usuario que hace la petición sea admin
            admin_user = self.user_repository.get_user_by_id(admin_user_id)
            if not admin_user or not admin_user.is_admin():
                return False, "Se requieren permisos de administrador", None
            
            # Buscar el usuario a modificar
            target_user = self.user_repository.get_user_by_id(user_id)
            if not target_user:
                return False, "Usuario no encontrado", None
            
            # No permitir que un admin cambie su propio rol
            if user_id == admin_user_id:
                return False, "No puedes cambiar tu propio rol", None
            
            # Actualizar el rol
            success = self.user_repository.update_user_role(user_id, new_role)
            if not success:
                return False, "Error al actualizar el rol del usuario", None
            
            # Obtener datos actualizados
            updated_user = self.user_repository.get_user_by_id(user_id)
            user_data = {
                "user_id": updated_user.user_id,
                "username": updated_user.username,
                "email": updated_user.email,
                "role": updated_user.role.value,
                "is_active": updated_user.is_active,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            logging.info(f"Admin {admin_user.username} cambió el rol de {target_user.username} a {new_role.value}")
            return True, f"Rol cambiado a {new_role.value} exitosamente", user_data
            
        except Exception as e:
            logging.error(f"Error al cambiar rol de usuario: {e}")
            return False, "Error interno del servidor", None
    
    def toggle_user_status(self, user_id: int, admin_user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Activar/desactivar un usuario (solo para administradores).
        
        Args:
            user_id (int): ID del usuario a modificar
            admin_user_id (int): ID del administrador que hace el cambio
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (éxito, mensaje, datos_usuario)
        """
        try:
            # Verificar que el usuario que hace la petición sea admin
            admin_user = self.user_repository.get_user_by_id(admin_user_id)
            if not admin_user or not admin_user.is_admin():
                return False, "Se requieren permisos de administrador", None
            
            # Buscar el usuario a modificar
            target_user = self.user_repository.get_user_by_id(user_id)
            if not target_user:
                return False, "Usuario no encontrado", None
            
            # No permitir que un admin se desactive a sí mismo
            if user_id == admin_user_id:
                return False, "No puedes desactivar tu propia cuenta", None
            
            # Cambiar el estado
            new_status = not target_user.is_active
            success = self.user_repository.update_user_status(user_id, new_status)
            if not success:
                return False, "Error al actualizar el estado del usuario", None
            
            # Obtener datos actualizados
            updated_user = self.user_repository.get_user_by_id(user_id)
            user_data = {
                "user_id": updated_user.user_id,
                "username": updated_user.username,
                "email": updated_user.email,
                "role": updated_user.role.value,
                "is_active": updated_user.is_active,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            status_text = "activado" if new_status else "desactivado"
            logging.info(f"Admin {admin_user.username} {status_text} al usuario {target_user.username}")
            return True, f"Usuario {status_text} exitosamente", user_data
            
        except Exception as e:
            logging.error(f"Error al cambiar estado de usuario: {e}")
            return False, "Error interno del servidor", None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtener un usuario por su ID.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            User: Objeto usuario o None si no existe
        """
        try:
            return self.user_repository.get_user_by_id(user_id)
        except Exception as e:
            logging.error(f"Error al obtener usuario por ID: {e}")
            return None

# Instancia global del servicio
user_service = UserService()