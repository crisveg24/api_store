"""
Configuración de fixtures y utilidades para tests

Este módulo proporciona fixtures compartidos y configuración para pytest.
"""
import pytest
import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Main import create_app
from config.database import Session, Base, engine
from models.user_model import User, UserRole
from utils.auth_utils import hash_password


@pytest.fixture(scope='session')
def app():
    """
    Fixture que crea una aplicación Flask para testing.
    Se crea una vez por sesión de tests.
    """
    # Crear app en modo testing
    flask_app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key-super-secure'
    })
    
    # Crear contexto de aplicación
    with flask_app.app_context():
        # Crear todas las tablas
        Base.metadata.create_all(engine)
        
        # Crear sesión
        session = Session()
        
        try:
            # Crear usuario de prueba (admin)
            admin_user = User(
                username='admin_test',
                email='admin@test.com',
                password_hash=hash_password('Admin123!'),
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(admin_user)
            
            # Crear usuario normal de prueba
            normal_user = User(
                username='user_test',
                email='user@test.com',
                password_hash=hash_password('User123!'),
                role=UserRole.USER,
                is_active=True
            )
            session.add(normal_user)
            
            # Crear usuario inactivo
            inactive_user = User(
                username='inactive_test',
                email='inactive@test.com',
                password_hash=hash_password('Inactive123!'),
                role=UserRole.USER,
                is_active=False
            )
            session.add(inactive_user)
            
            session.commit()
        finally:
            session.close()
        
        yield flask_app
        
        # Cleanup: Eliminar todas las tablas después de los tests
        Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def client(app):
    """
    Fixture que proporciona un cliente de testing.
    Se crea para cada función de test.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """
    Fixture que proporciona un CLI runner de testing.
    """
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def admin_token(client):
    """
    Fixture que obtiene un token JWT válido de administrador.
    """
    response = client.post('/api/users/login', json={
        'identifier': 'admin_test',
        'password': 'Admin123!'
    })
    data = response.get_json()
    return data['data']['access_token']


@pytest.fixture(scope='function')
def user_token(client):
    """
    Fixture que obtiene un token JWT válido de usuario normal.
    """
    response = client.post('/api/users/login', json={
        'identifier': 'user_test',
        'password': 'User123!'
    })
    data = response.get_json()
    return data['data']['access_token']


@pytest.fixture(scope='function')
def auth_headers_admin(admin_token):
    """
    Fixture que proporciona headers de autenticación con token de admin.
    """
    return {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture(scope='function')
def auth_headers_user(user_token):
    """
    Fixture que proporciona headers de autenticación con token de usuario.
    """
    return {
        'Authorization': f'Bearer {user_token}',
        'Content-Type': 'application/json'
    }
