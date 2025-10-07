# Sistema de Gestión de Tiendas con Autenticación

Este proyecto es una API completa para la gestión de tiendas con sistema de autenticación y autorización basado en JWT. Implementado siguiendo el patrón arquitectónico por capas con Python, Flask, SQLAlchemy y seguridad moderna. Incluye una interfaz web administrativa completa para gestión de tiendas y usuarios.

## 🚀 Características Principales

### 🏪 Gestión de Tiendas
- **API RESTful** para CRUD completo de tiendas
- **Paginación** optimizada para grandes volúmenes de datos (12,545+ tiendas)
- **Búsqueda avanzada** por todos los campos
- **Filtros múltiples** (área, inventario, clientes, ventas)
- **Estadísticas en tiempo real** con panel visual
- **Gráficos interactivos** con Chart.js (próximamente)
- **Exportación a CSV** (próximamente)
- **Validación** de datos y manejo de errores

### � Gestión de Usuarios (Panel Admin)
- **Lista completa** de usuarios con roles y estados
- **Cambio de roles** (User ↔ Admin)
- **Activación/desactivación** de cuentas
- **Eliminación** de usuarios
- **Estadísticas** de usuarios activos

### �🔐 Sistema de Autenticación y Autorización
- **JWT Tokens** para autenticación segura
- **Roles de usuario**: Administrador y Usuario
- **Hash de contraseñas** con bcrypt
- **Protección de endpoints** por roles
- **Validación** robusta de credenciales
- **Sesión persistente** con verificación automática

### 🏗️ Arquitectura por Capas
- **Modelos**: Definición clara de entidades (Store, User)
- **Repositorios**: Acceso a datos desacoplado
- **Servicios**: Lógica de negocio centralizada
- **Controladores**: Endpoints y validación de entrada
- **Configuración**: Gestión centralizada de configuraciones

### 🎨 Interfaz Web Administrativa
- **Dashboard responsivo** con diseño moderno
- **Sistema de pestañas** (Tiendas, Usuarios, Estadísticas)
- **Tarjetas interactivas** con acciones rápidas
- **Modales** para crear y editar tiendas
- **Iconos** con Lucide Icons
- **Notificaciones** visuales de operaciones
- **Tema oscuro** profesional

## 📁 Estructura del Proyecto

```
api_store/
├── 📱 Main.py                     # Aplicación principal Flask
├── 🔧 create_admin.py             # Script para crear usuario admin
├── 📋 requirements.txt            # Dependencias del proyecto
├── 🗄️ stores.db                   # Base de datos SQLite (12,545+ tiendas)
├── 📝 README.md                   # Documentación completa
├── 🚫 .gitignore                  # Archivos excluidos del repositorio
│
├── 📊 models/                     # Modelos de datos
│   ├── store_model.py             # Modelo de tienda con validaciones
│   └── user_model.py              # Modelo de usuario con roles y estado
│
├── 🗃️ repositories/               # Capa de acceso a datos
│   ├── store_repository.py        # Repositorio de tiendas (búsqueda, filtros)
│   └── user_repository.py         # Repositorio de usuarios
│
├── 🔧 services/                   # Lógica de negocio
│   ├── store_service.py           # Servicios de tiendas con estadísticas
│   └── user_service.py            # Servicios de usuarios con validaciones
│
├── 🌐 controllers/                # Controladores de API
│   ├── store_controller.py        # Endpoints de tiendas con filtros
│   └── user_controller.py         # Endpoints de usuarios y autenticación
│
├── ⚙️ config/                     # Configuraciones
│   ├── database.py                # Configuración de BD SQLAlchemy
│   ├── auth_config.py             # Configuración de autenticación
│   ├── jwt_config.py              # Configuración de JWT
│   └── files/                     # Archivos de datos
│       └── Stores.csv             # Datos iniciales de tiendas
│
├── 🔧 utils/                      # Utilidades
│   ├── auth_utils.py              # Hash de contraseñas, validaciones
│   └── auth_decorators.py         # Decoradores de seguridad JWT
│
├── 🎨 static/                     # Archivos estáticos
│   ├── script.js                  # JavaScript frontend (búsqueda, filtros, modales)
│   └── styles.css                 # Estilos CSS personalizados
│
└── 📄 templates/                  # Plantillas HTML
    └── index.html                 # Interfaz web administrativa completa
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
| POST | `/api/users/login` | Iniciar sesión (retorna JWT) | ❌ Público |
| GET | `/api/users/profile` | Obtener perfil del usuario actual | ✅ Token requerido |
| PUT | `/api/users/profile` | Actualizar perfil (nombre, email, password) | ✅ Token requerido |
| GET | `/api/users/verify-token` | Verificar validez del token | ✅ Token requerido |

### 👥 Gestión de Usuarios (Solo Admins)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/users/` | Listar todos los usuarios con filtros | 🔒 Admin requerido |
| PUT | `/api/users/{id}/role` | Cambiar rol de usuario (User/Admin) | 🔒 Admin requerido |
| PUT | `/api/users/{id}/toggle-status` | Activar/desactivar usuario | 🔒 Admin requerido |
| DELETE | `/api/users/{id}` | Eliminar usuario permanentemente | 🔒 Admin requerido |

### 🏪 Gestión de Tiendas

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/stores` | Listar tiendas (paginado, búsqueda, filtros) | ❌ Público |
| GET | `/api/stores/{id}` | Obtener tienda específica por ID | ❌ Público |
| POST | `/api/stores` | Crear nueva tienda | 🔒 Admin requerido |
| PUT | `/api/stores/{id}` | Actualizar tienda existente | 🔒 Admin requerido |
| DELETE | `/api/stores/{id}` | Eliminar tienda (próximamente) | 🔒 Admin requerido |
| GET | `/api/stores/stats` | Estadísticas completas de tiendas | 🔒 Admin requerido |

### 📊 Parámetros de Búsqueda y Filtros

**GET /api/stores** acepta los siguientes parámetros:

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `page` | int | Número de página (default: 1) | `?page=2` |
| `per_page` | int | Items por página (default: 10, max: 100) | `?per_page=20` |
| `search` | string | Búsqueda en todos los campos | `?search=150` |
| `min_area` | float | Área mínima | `?min_area=100` |
| `max_area` | float | Área máxima | `?max_area=500` |
| `min_items` | int | Items disponibles mínimos | `?min_items=10` |
| `max_items` | int | Items disponibles máximos | `?max_items=100` |
| `min_customers` | int | Clientes diarios mínimos | `?min_customers=50` |
| `max_customers` | int | Clientes diarios máximos | `?max_customers=500` |
| `min_sales` | float | Ventas mínimas | `?min_sales=1000` |
| `max_sales` | float | Ventas máximas | `?max_sales=50000` |

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

### 3. Listar Tiendas (con paginación y filtros)
```bash
# Paginación simple
GET /api/stores?page=1&per_page=10

# Con búsqueda
GET /api/stores?search=150&page=1

# Con filtros múltiples
GET /api/stores?min_area=100&max_area=500&min_sales=10000&page=1
```

### 4. Obtener Estadísticas (requiere admin)
```bash
GET /api/stores/stats
Authorization: Bearer <token>

# Respuesta:
{
    "success": true,
    "data": {
        "total_stores": 12545,
        "total_area": 1567890.50,
        "total_items": 625000,
        "total_daily_customers": 2500000,
        "total_sales": 156789000.00,
        "avg_store_area": 125.50,
        "avg_items": 50,
        "avg_customers": 200,
        "avg_sales": 12500.00
    }
}
```

### 5. Crear Tienda (requiere admin)
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

### 6. Gestión de Usuarios (requiere admin)
```bash
# Listar usuarios
GET /api/users/
Authorization: Bearer <token>

# Cambiar rol de usuario
PUT /api/users/2/role
Authorization: Bearer <token>
Content-Type: application/json
{
    "role": "admin"
}

# Desactivar usuario
PUT /api/users/2/toggle-status
Authorization: Bearer <token>
```

## 🗄️ Base de Datos

### Tablas Principales

#### Tabla `stores`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER | ID único (Primary Key) |
| `store_area` | FLOAT | Área de la tienda (m²) |
| `items_available` | INTEGER | Número de items disponibles |
| `daily_customer_count` | INTEGER | Clientes diarios promedio |
| `store_sales` | FLOAT | Ventas de la tienda ($) |

#### Tabla `users`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER | ID único (Primary Key) |
| `username` | VARCHAR(50) | Nombre de usuario único |
| `email` | VARCHAR(100) | Email único |
| `password_hash` | VARCHAR(255) | Hash bcrypt de la contraseña |
| `role` | ENUM | Rol: 'user' o 'admin' |
| `is_active` | BOOLEAN | Estado de la cuenta |
| `created_at` | DATETIME | Fecha de creación |

### Estadísticas Actuales
- **12,545+ tiendas** en la base de datos
- **4 usuarios** registrados (2 admins, 2 users)
- **Índices optimizados** para búsquedas rápidas

### Tecnología
- **SQLite**: Base de datos local para desarrollo
- **SQLAlchemy**: ORM para manejo de datos
- **Migraciones**: Automáticas al iniciar aplicación
- **Índices**: Optimizados para búsqueda y filtros

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
DATABASE_URL=sqlite:///stores.db
```

### Configuración de Producción
- Cambiar `SECRET_KEY` por una clave segura aleatoria
- Configurar base de datos externa (PostgreSQL/MySQL)
- Establecer `debug=False` en `Main.py`
- Usar servidor WSGI (Gunicorn, uWSGI)
- Configurar CORS adecuadamente
- Implementar rate limiting

### Funcionalidades Próximas

#### ✅ Implementadas
- [x] Sistema de autenticación JWT completo
- [x] Gestión de usuarios con roles
- [x] CRUD de tiendas con paginación
- [x] Búsqueda y filtros avanzados
- [x] Panel de estadísticas
- [x] Interfaz web administrativa

#### 🚧 En Desarrollo
- [ ] **Gráficos en Estadísticas**: Visualización con Chart.js (barras, líneas, distribuciones)
- [ ] **Funcionalidad de Eliminar Tiendas**: Conectar backend con frontend con confirmación
- [ ] **Exportación a CSV**: Descargar datos de tiendas filtradas

#### 💡 Planificadas
- [ ] Sistema de auditoría (logs de cambios)
- [ ] Importación masiva de tiendas desde CSV
- [ ] Dashboard de métricas en tiempo real
- [ ] Notificaciones por email
- [ ] API de reportes avanzados

## 🤝 Contribuciones

Contribuciones son bienvenidas! Por favor sigue estos pasos:

1. Fork del repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios con mensaje descriptivo (`git commit -m 'feat: Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request detallado

### Convenciones de Commits
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bugs
- `docs:` Cambios en documentación
- `style:` Formateo, punto y coma faltante, etc.
- `refactor:` Refactorización de código
- `test:` Agregar tests
- `chore:` Actualizar tareas de build, configuraciones, etc.

## 📊 Tecnologías Utilizadas

### Backend
- **Python 3.x** - Lenguaje principal
- **Flask** - Framework web
- **SQLAlchemy** - ORM
- **SQLite** - Base de datos
- **PyJWT** - Manejo de JWT tokens
- **bcrypt** - Hash de contraseñas
- **Flask-CORS** - Manejo de CORS

### Frontend
- **HTML5 & CSS3** - Estructura y estilos
- **JavaScript (ES6+)** - Lógica del cliente
- **jQuery** - Manipulación del DOM
- **Lucide Icons** - Iconografía
- **Chart.js** - Gráficos (próximamente)

### Herramientas
- **Git** - Control de versiones
- **GitHub** - Repositorio remoto
- **VS Code** - IDE recomendado
- **Postman** - Testing de API

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas:

1. **Documentación**: Revisa este README completo
2. **Logs**: Verifica los logs de la aplicación en la consola
3. **Issues**: Crea un issue en el repositorio de GitHub
4. **Información**: Proporciona detalles del error, logs y pasos para reproducir

### Problemas Comunes

#### Error de autenticación
- Verifica que el token JWT sea válido y no haya expirado
- Asegúrate de incluir el header `Authorization: Bearer <token>`

#### Error de base de datos
- Verifica que `stores.db` exista en el directorio raíz
- Ejecuta `python Main.py` para crear/actualizar las tablas

#### Error de permisos
- Verifica que tu usuario tenga el rol `admin` para operaciones administrativas
- Usa el script `create_admin.py` para crear un usuario administrador

---

## 📈 Estado del Proyecto

**Versión**: 1.0.0 (En desarrollo activo)
**Branch Principal**: `Development`
**Última Actualización**: Octubre 2025

### Próximas Actualizaciones
1. **v1.1.0**: Gráficos interactivos con Chart.js
2. **v1.2.0**: Funcionalidad de eliminación con confirmación
3. **v1.3.0**: Exportación a CSV de datos filtrados

---

**¡Desarrollado con perrenque usando Flask, SQLAlchemy y las mejores prácticas de seguridad y arquitectura de software!**

---

## 📝 Changelog

### [1.0.0] - 2025-10-07
#### Added
- Sistema completo de autenticación y autorización con JWT
- Gestión de tiendas con CRUD completo
- Búsqueda avanzada y filtros múltiples
- Panel de estadísticas en tiempo real
- Gestión de usuarios con roles
- Interfaz web administrativa responsiva
- Paginación optimizada para grandes volúmenes
- Validación de datos robusta
- Hash de contraseñas con bcrypt

#### Changed
- Arquitectura por capas (Modelos, Repositorios, Servicios, Controladores)
- Optimización de consultas a base de datos
- Mejoras en la experiencia de usuario

#### Security
- Implementación de JWT con expiración
- Protección de endpoints sensibles
- Validación de contraseñas con requisitos de seguridad
- Sanitización de entradas de usuario