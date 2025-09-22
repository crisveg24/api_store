# Sistema de Gestión de Tiendas con Autenticación

Este proyecto es una API completa para la gestión de tiendas con sistema de autenticación y autorización basado en JWT. Implementado siguiendo el patrón arquitectónico por capas con Python, Flask, SQLAlchemy y seguridad moderna.

## 🚀 Características Principales

### 🏪 Gestión de Tiendas
- **API RESTful** para CRUD completo de tiendas
- **Paginación** optimizada para grandes volúmenes de datos
- **Estadísticas** y análisis de tiendas (solo admins)
- **Validación** de datos y manejo de errores

### 🔐 Sistema de Autenticación y Autorización
- **JWT Tokens** para autenticación segura
- **Roles de usuario**: Administrador y Usuario
- **Hash de contraseñas** con bcrypt
- **Protección de endpoints** por roles
- **Validación** robusta de credenciales

### 🏗️ Arquitectura por Capas
- **Modelos**: Definición clara de entidades (Store, User)
- **Repositorios**: Acceso a datos desacoplado
- **Servicios**: Lógica de negocio centralizada
- **Controladores**: Endpoints y validación de entrada
- **Configuración**: Gestión centralizada de configuraciones

## 📁 Estructura del Proyecto

```
api_store/
├── 📱 Main.py                     # Aplicación principal Flask
├── 🔧 create_admin.py             # Script para crear usuario admin
├── 📋 requirements.txt            # Dependencias del proyecto
├── 🗄️ stores.db                   # Base de datos SQLite
│
├── 📊 models/                     # Modelos de datos
│   ├── store_model.py             # Modelo de tienda
│   └── user_model.py              # Modelo de usuario con roles
│
├── 🗃️ repositories/               # Capa de acceso a datos
│   ├── store_repository.py        # Repositorio de tiendas
│   └── user_repository.py         # Repositorio de usuarios
│
├── 🔧 services/                   # Lógica de negocio
│   ├── store_service.py           # Servicios de tiendas
│   └── user_service.py            # Servicios de usuarios
│
├── 🌐 controllers/                # Controladores de API
│   ├── store_controller.py        # Endpoints de tiendas
│   └── user_controller.py         # Endpoints de usuarios
│
├── ⚙️ config/                     # Configuraciones
│   ├── database.py                # Configuración de BD
│   ├── auth_config.py             # Configuración de autenticación
│   └── files/                     # Archivos de datos
│       └── Stores_clean.csv       # Datos iniciales de tiendas
│
├── 🔧 utils/                      # Utilidades
│   ├── auth_utils.py              # Utilidades de autenticación
│   └── auth_decorators.py         # Decoradores de seguridad
│
├── 🎨 static/                     # Archivos estáticos
│   ├── script.js                  # JavaScript frontend
│   └── styles.css                 # Estilos CSS
│
└── 📄 templates/                  # Plantillas HTML
    └── index.html                 # Interfaz web
```

## 🛠️ Instalación y Configuración

### 1. Crear y Activar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar en Windows
.venv\Scripts\Activate.ps1

# Activar en Linux/Mac
source .venv/bin/activate
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Crear Usuario Administrador

```bash
# Opción 1: Script interactivo
python create_admin.py

# Opción 2: Endpoint directo (después de iniciar servidor)
# POST http://localhost:5000/api/users/create-admin
```

### 4. Iniciar Aplicación

```bash
python Main.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 🔑 Credenciales por Defecto

**Usuario Administrador:**
- Username: `admin`
- Email: `admin@tienda.com`
- Password: `Admin123!`

## 📡 Endpoints de la API

### 🔐 Autenticación

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| POST | `/api/users/register` | Registrar nuevo usuario | ❌ Público |
| POST | `/api/users/login` | Iniciar sesión | ❌ Público |
| GET | `/api/users/profile` | Obtener perfil | ✅ Token requerido |
| PUT | `/api/users/profile` | Actualizar perfil | ✅ Token requerido |
| GET | `/api/users/verify-token` | Verificar token | ✅ Token requerido |

### 👥 Gestión de Usuarios (Solo Admins)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/users/` | Listar todos los usuarios | 🔒 Admin requerido |
| PUT | `/api/users/{id}/role` | Cambiar rol de usuario | 🔒 Admin requerido |
| PUT | `/api/users/{id}/toggle-status` | Activar/desactivar usuario | 🔒 Admin requerido |
| DELETE | `/api/users/{id}` | Eliminar usuario | 🔒 Admin requerido |

### 🏪 Gestión de Tiendas

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/stores` | Listar tiendas (paginado) | ❌ Público |
| GET | `/api/stores/{id}` | Obtener tienda específica | ❌ Público |
| POST | `/api/stores` | Crear nueva tienda | 🔒 Admin requerido |
| PUT | `/api/stores/{id}` | Actualizar tienda | 🔒 Admin requerido |
| DELETE | `/api/stores/{id}` | Eliminar tienda | 🔒 Admin requerido |
| GET | `/api/stores/stats` | Estadísticas de tiendas | 🔒 Admin requerido |

## 🔒 Sistema de Autenticación

### JWT Tokens
- **Algoritmo**: HS256
- **Expiración**: 24 horas (configurable)
- **Header**: `Authorization: Bearer <token>`

### Roles de Usuario
- **USER**: Acceso de solo lectura a tiendas
- **ADMIN**: Acceso completo (CRUD tiendas + gestión usuarios)

### Seguridad de Contraseñas
- **Hash**: bcrypt con salt automático
- **Validación**: Mínimo 8 caracteres, mayúscula, minúscula, número, símbolo
- **Protección**: Cambio de contraseña requiere contraseña actual

## 📝 Ejemplos de Uso

### 1. Registro de Usuario
```bash
POST /api/users/register
Content-Type: application/json

{
    "username": "usuario1",
    "email": "usuario1@ejemplo.com",
    "password": "MiPassword123!"
}
```

### 2. Login
```bash
POST /api/users/login
Content-Type: application/json

{
    "identifier": "admin",
    "password": "Admin123!"
}

# Respuesta:
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "user_id": 1,
        "username": "admin",
        "role": "admin"
    }
}
```

### 3. Listar Tiendas (con paginación)
```bash
GET /api/stores?page=1&per_page=10
```

### 4. Crear Tienda (requiere admin)
```bash
POST /api/stores
Authorization: Bearer <token>
Content-Type: application/json

{
    "store_area": 150.5,
    "items_available": 50,
    "daily_customer_count": 200,
    "store_sales": 15000.00
}
```

## 🗄️ Base de Datos

### Tablas Principales
- **stores**: Información de tiendas
- **users**: Usuarios del sistema con roles

### Tecnología
- **SQLite**: Base de datos local para desarrollo
- **SQLAlchemy**: ORM para manejo de datos
- **Migraciones**: Automáticas al iniciar aplicación

## 🛡️ Seguridad Implementada

### Autenticación
- ✅ JWT tokens con expiración
- ✅ Hash seguro de contraseñas (bcrypt)
- ✅ Validación robusta de credenciales

### Autorización
- ✅ Decoradores de protección de endpoints
- ✅ Roles diferenciados (admin/user)
- ✅ Verificación de permisos por acción

### Validación
- ✅ Validación de entrada en todos los endpoints
- ✅ Sanitización de datos
- ✅ Manejo seguro de errores

## 🔧 Configuración Avanzada

### Variables de Entorno
Crea un archivo `.env` para configuraciones personalizadas:

```env
SECRET_KEY=tu-clave-secreta-muy-segura
JWT_EXPIRATION_HOURS=24
BCRYPT_ROUNDS=12
```

### Configuración de Producción
- Cambiar `SECRET_KEY` por una clave segura
- Configurar base de datos externa (PostgreSQL/MySQL)
- Establecer `debug=False` en `Main.py`
- Usar servidor WSGI (Gunicorn, uWSGI)

## 🤝 Contribuciones

1. Fork del repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la documentación
2. Verifica los logs de la aplicación
3. Crea un issue en el repositorio
4. Proporciona información detallada del error

---

**¡Desarrollado con ❤️ usando Flask, SQLAlchemy y las mejores prácticas de seguridad!**