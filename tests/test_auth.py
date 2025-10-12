"""
Tests de Autenticación

Este módulo contiene tests para verificar el sistema de autenticación:
- Login con credenciales válidas
- Login con credenciales inválidas
- Registro de usuarios
- Acceso a rutas protegidas con y sin token
"""
import pytest


class TestLogin:
    """Tests relacionados con el login de usuarios"""
    
    def test_login_con_credenciales_validas_username(self, client):
        """
        Test 1: Login con credenciales válidas usando username
        
        Verifica que:
        - El endpoint responde con status 200
        - Se retorna un access_token
        - Los datos del usuario son correctos
        """
        response = client.post('/api/users/login', json={
            'identifier': 'admin_test',
            'password': 'Admin123!'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert data['data']['username'] == 'admin_test'
        assert data['data']['role'] == 'admin'
        assert data['data']['token_type'] == 'bearer'
    
    def test_login_con_credenciales_validas_email(self, client):
        """
        Test 2: Login con credenciales válidas usando email
        
        Verifica que:
        - El login funciona tanto con username como con email
        - Se retorna un token válido
        """
        response = client.post('/api/users/login', json={
            'identifier': 'user@test.com',
            'password': 'User123!'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert data['data']['email'] == 'user@test.com'
        assert data['data']['role'] == 'user'
    
    def test_login_con_password_incorrecta(self, client):
        """
        Test 3: Login con contraseña incorrecta
        
        Verifica que:
        - El endpoint responde con status 401
        - No se retorna token
        - Se muestra mensaje de error apropiado
        """
        response = client.post('/api/users/login', json={
            'identifier': 'admin_test',
            'password': 'ContraseñaIncorrecta123!'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        
        assert data['success'] is False
        assert 'access_token' not in data.get('data', {})
        assert 'credenciales' in data['message'].lower() or 'password' in data['message'].lower()
    
    def test_login_con_usuario_inexistente(self, client):
        """
        Test 4: Login con usuario que no existe
        
        Verifica que:
        - El endpoint responde con status 401
        - Se muestra mensaje de error apropiado
        """
        response = client.post('/api/users/login', json={
            'identifier': 'usuario_que_no_existe',
            'password': 'Password123!'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        
        assert data['success'] is False
        assert 'access_token' not in data.get('data', {})
    
    def test_login_con_usuario_inactivo(self, client):
        """
        Test 5: Login con usuario inactivo
        
        Verifica que:
        - Los usuarios inactivos no pueden hacer login
        - Se muestra mensaje apropiado
        """
        response = client.post('/api/users/login', json={
            'identifier': 'inactive_test',
            'password': 'Inactive123!'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        
        assert data['success'] is False
        assert 'inactiv' in data['message'].lower() or 'desactivad' in data['message'].lower()
    
    def test_login_sin_datos(self, client):
        """
        Test 6: Login sin enviar datos
        
        Verifica que:
        - El endpoint valida los datos requeridos
        - Responde con status 400
        """
        response = client.post('/api/users/login', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
    
    def test_login_sin_password(self, client):
        """
        Test 7: Login sin contraseña
        
        Verifica que:
        - El endpoint valida que la contraseña es requerida
        """
        response = client.post('/api/users/login', json={
            'identifier': 'admin_test'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False


class TestRegistro:
    """Tests relacionados con el registro de usuarios"""
    
    def test_registro_exitoso(self, client):
        """
        Test 8: Registro exitoso de un nuevo usuario
        
        Verifica que:
        - Se puede registrar un usuario con datos válidos
        - El usuario se crea con rol 'user' por defecto
        - No se retorna la contraseña en la respuesta
        """
        response = client.post('/api/users/register', json={
            'username': 'nuevo_usuario',
            'email': 'nuevo@test.com',
            'password': 'Password123!'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['username'] == 'nuevo_usuario'
        assert data['data']['email'] == 'nuevo@test.com'
        assert data['data']['role'] == 'user'
        assert 'password' not in data['data']
        assert 'password_hash' not in data['data']
    
    def test_registro_con_email_duplicado(self, client):
        """
        Test 9: Registro con email que ya existe
        
        Verifica que:
        - No se puede registrar un usuario con email duplicado
        - Se muestra mensaje de error apropiado
        """
        response = client.post('/api/users/register', json={
            'username': 'nuevo_usuario_2',
            'email': 'admin@test.com',  # Email ya existente
            'password': 'Password123!'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'email' in data['message'].lower()
    
    def test_registro_con_username_duplicado(self, client):
        """
        Test 10: Registro con username que ya existe
        
        Verifica que:
        - No se puede registrar un usuario con username duplicado
        """
        response = client.post('/api/users/register', json={
            'username': 'admin_test',  # Username ya existente
            'email': 'otroemail@test.com',
            'password': 'Password123!'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
    
    def test_registro_con_datos_incompletos(self, client):
        """
        Test 11: Registro sin todos los datos requeridos
        
        Verifica que:
        - Se validan todos los campos requeridos
        """
        response = client.post('/api/users/register', json={
            'username': 'usuario_incompleto'
            # Faltan email y password
        })
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False


class TestRutasProtegidas:
    """Tests relacionados con el acceso a rutas protegidas"""
    
    def test_acceso_a_perfil_con_token_valido(self, client, auth_headers_user):
        """
        Test 12: Acceso a ruta protegida con token válido
        
        Verifica que:
        - Un usuario con token válido puede acceder a su perfil
        - Se retornan los datos correctos del usuario
        """
        response = client.get('/api/users/profile', headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['username'] == 'user_test'
        assert data['data']['email'] == 'user@test.com'
    
    def test_acceso_a_perfil_sin_token(self, client):
        """
        Test 13: Acceso a ruta protegida sin token
        
        Verifica que:
        - Sin token, no se puede acceder a rutas protegidas
        - Se retorna status 401
        """
        response = client.get('/api/users/profile')
        
        assert response.status_code == 401
        data = response.get_json()
        
        # Flask-JWT-Extended retorna este formato de error
        assert 'msg' in data or 'message' in data
    
    def test_acceso_a_perfil_con_token_invalido(self, client):
        """
        Test 14: Acceso a ruta protegida con token inválido
        
        Verifica que:
        - Un token inválido no permite acceso
        - Se retorna error 422 o 401
        """
        headers = {
            'Authorization': 'Bearer token_invalido_12345',
            'Content-Type': 'application/json'
        }
        response = client.get('/api/users/profile', headers=headers)
        
        # Flask-JWT-Extended retorna 422 para tokens malformados
        assert response.status_code in [401, 422]
    
    def test_acceso_a_perfil_con_token_expirado(self, client):
        """
        Test 15: Acceso con token expirado
        
        Nota: Este test requeriría manipular el tiempo o generar un token expirado.
        Por simplicidad, usamos un token JWT válido pero generado con una clave diferente.
        """
        # Token generado con una clave diferente (simula token expirado/inválido)
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U',
            'Content-Type': 'application/json'
        }
        response = client.get('/api/users/profile', headers=headers)
        
        assert response.status_code in [401, 422]


class TestAutorizacionPorRoles:
    """Tests relacionados con la autorización por roles"""
    
    def test_usuario_normal_puede_ver_tiendas(self, client, auth_headers_user):
        """
        Test 16: Usuario normal puede acceder a endpoints públicos
        
        Verifica que:
        - Los usuarios normales pueden ver tiendas (lectura)
        """
        response = client.get('/api/stores?page=1&per_page=5', headers=auth_headers_user)
        
        # Este endpoint es público, pero verificamos que funciona con token
        assert response.status_code == 200
    
    def test_usuario_normal_no_puede_crear_tiendas(self, client, auth_headers_user):
        """
        Test 17: Usuario normal NO puede crear tiendas (solo admins)
        
        Verifica que:
        - La autorización por roles funciona
        - Los usuarios normales reciben 403
        """
        response = client.post('/api/stores', 
                              headers=auth_headers_user,
                              json={
                                  'store_area': 150.5,
                                  'items_available': 50,
                                  'daily_customer_count': 200,
                                  'store_sales': 15000.00
                              })
        
        assert response.status_code == 403
        data = response.get_json()
        
        assert data['success'] is False
    
    def test_admin_puede_crear_tiendas(self, client, auth_headers_admin):
        """
        Test 18: Administrador puede crear tiendas
        
        Verifica que:
        - Los administradores tienen permisos completos
        """
        response = client.post('/api/stores',
                              headers=auth_headers_admin,
                              json={
                                  'store_area': 200.0,
                                  'items_available': 75,
                                  'daily_customer_count': 300,
                                  'store_sales': 25000.00
                              })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['success'] is True
    
    def test_admin_puede_listar_usuarios(self, client, auth_headers_admin):
        """
        Test 19: Administrador puede listar usuarios
        
        Verifica que:
        - Los endpoints de administración requieren rol admin
        """
        response = client.get('/api/users/', headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    def test_usuario_normal_no_puede_listar_usuarios(self, client, auth_headers_user):
        """
        Test 20: Usuario normal NO puede listar usuarios
        
        Verifica que:
        - La autorización por roles protege endpoints de admin
        """
        response = client.get('/api/users/', headers=auth_headers_user)
        
        assert response.status_code == 403
        data = response.get_json()
        
        assert data['success'] is False
        assert 'permisos' in data['message'].lower() or 'admin' in data['message'].lower()


class TestVerificacionToken:
    """Tests relacionados con la verificación de tokens"""
    
    def test_verificar_token_valido(self, client, auth_headers_admin):
        """
        Test 21: Verificar un token válido
        
        Verifica que:
        - El endpoint /verify-token funciona correctamente
        - Retorna información del usuario
        """
        response = client.get('/api/users/verify-token', headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['username'] == 'admin_test'
        assert data['data']['role'] == 'admin'
    
    def test_verificar_token_sin_token(self, client):
        """
        Test 22: Verificar token sin enviar token
        
        Verifica que:
        - El endpoint requiere autenticación
        """
        response = client.get('/api/users/verify-token')
        
        assert response.status_code == 401


class TestActualizacionPerfil:
    """Tests relacionados con la actualización de perfil"""
    
    def test_actualizar_email_propio(self, client, auth_headers_user):
        """
        Test 23: Usuario puede actualizar su propio email
        
        Verifica que:
        - Los usuarios pueden modificar su perfil
        """
        response = client.put('/api/users/profile',
                             headers=auth_headers_user,
                             json={'email': 'nuevo_email@test.com'})
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['email'] == 'nuevo_email@test.com'
    
    def test_cambiar_password_sin_password_actual(self, client, auth_headers_user):
        """
        Test 24: No se puede cambiar password sin proporcionar el actual
        
        Verifica que:
        - Cambiar contraseña requiere la contraseña actual
        """
        response = client.put('/api/users/profile',
                             headers=auth_headers_user,
                             json={'new_password': 'NuevoPassword123!'})
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
