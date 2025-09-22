"""
Script para crear usuario administrador

Este script crea un usuario administrador por defecto en la base de datos.
Útil para la configuración inicial del sistema.
"""
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import create_tables, initialize_data
from services.user_service import user_service
from models.user_model import UserRole
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user():
    """
    Crear un usuario administrador por defecto.
    """
    try:
        # Asegurar que las tablas existan
        logger.info("Verificando/creando tablas de base de datos...")
        create_tables()
        
        # Datos del administrador por defecto
        admin_data = {
            'username': 'admin',
            'email': 'admin@tienda.com',
            'password': 'Admin123!'
        }
        
        print("\n" + "="*50)
        print("CREACIÓN DE USUARIO ADMINISTRADOR")
        print("="*50)
        
        # Verificar si ya existe un administrador
        logger.info("Verificando si ya existe un administrador...")
        from repositories.user_repository import user_repository
        admin_users = user_repository.get_users_by_role(UserRole.ADMIN)
        
        if admin_users:
            print(f"⚠️  Ya existe(n) {len(admin_users)} usuario(s) administrador(es):")
            for admin in admin_users:
                status = "✅ ACTIVO" if admin.is_active else "❌ INACTIVO"
                print(f"   - {admin.username} ({admin.email}) - {status}")
            
            print("\n¿Desea crear otro administrador? (s/N): ", end="")
            response = input().strip().lower()
            
            if response not in ['s', 'si', 'sí', 'y', 'yes']:
                print("Operación cancelada.")
                return
        
        print("\nIngrese los datos del administrador (presione Enter para usar valores por defecto):")
        
        # Solicitar datos del usuario
        username = input(f"Username [{admin_data['username']}]: ").strip()
        if not username:
            username = admin_data['username']
        
        email = input(f"Email [{admin_data['email']}]: ").strip()
        if not email:
            email = admin_data['email']
        
        password = input(f"Password [{admin_data['password']}]: ").strip()
        if not password:
            password = admin_data['password']
        
        # Crear el administrador
        print(f"\n🔄 Creando usuario administrador '{username}'...")
        
        success, message, user_data = user_service.register_user(
            username=username,
            email=email,
            password=password,
            role=UserRole.ADMIN
        )
        
        if success:
            print("✅ ¡Usuario administrador creado exitosamente!")
            print(f"   Username: {user_data['username']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Role: {user_data['role']}")
            print(f"   ID: {user_data['user_id']}")
            print(f"   Creado: {user_data['created_at']}")
            
            print("\n📋 CREDENCIALES DE ACCESO:")
            print(f"   Username/Email: {username}")
            print(f"   Password: {password}")
            
            print("\n🌐 ENDPOINTS DISPONIBLES:")
            print("   Login: POST http://localhost:5000/api/users/login")
            print("   Perfil: GET http://localhost:5000/api/users/profile")
            print("   Usuarios: GET http://localhost:5000/api/users/")
            print("   Tiendas: GET http://localhost:5000/api/stores")
            print("   Crear tienda: POST http://localhost:5000/api/stores")
            
        else:
            print(f"❌ Error al crear usuario administrador: {message}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """
    Función principal del script.
    """
    print("🏪 SISTEMA DE GESTIÓN DE TIENDAS - SETUP INICIAL")
    print("Script para crear usuario administrador\n")
    
    try:
        # Crear administrador
        success = create_admin_user()
        
        if success:
            print("\n🎉 ¡Configuración completada exitosamente!")
            print("\nPuede iniciar la aplicación con:")
            print("   python Main.py")
            print("\nY acceder a:")
            print("   http://localhost:5000/")
        else:
            print("\n❌ La configuración no se completó correctamente.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error en main: {e}")
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()