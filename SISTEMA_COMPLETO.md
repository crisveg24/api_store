# 🏪 Sistema Completo de Gestión de Tiendas con Autenticación

## 📋 Resumen del Sistema

El sistema de gestión de tiendas ahora incluye **autenticación completa** con roles de usuario, protección de endpoints y una interfaz web moderna y responsive.

## 🔐 Características de Autenticación

### **Backend Implementado:**
- ✅ **JWT Tokens** - Autenticación segura con expiración
- ✅ **Bcrypt** - Hashing de contraseñas 
- ✅ **Roles de Usuario** - Admin y Usuario regular
- ✅ **Middleware de Protección** - Decoradores de autenticación
- ✅ **Endpoints Seguros** - CRUD protegido por roles

### **Frontend Implementado:**
- ✅ **Formularios de Login/Registro** - UI moderna y responsive
- ✅ **Gestión de Tokens JWT** - Almacenamiento y verificación automática
- ✅ **Control de Acceso por Roles** - UI adaptativa según permisos
- ✅ **Notificaciones en Tiempo Real** - Feedback instantáneo al usuario
- ✅ **Gestión de Sesiones** - Login/logout automático

## 🚀 Funcionalidades del Sistema

### **Para Usuarios Regulares:**
- 📊 **Ver tiendas** con paginación avanzada
- 🔍 **Filtros y búsqueda** de tiendas
- 📱 **Interfaz responsive** para móviles
- 🔐 **Gestión de perfil** de usuario

### **Para Administradores:**
- 👑 **Todas las funciones de usuario** +
- ➕ **Crear nuevas tiendas**
- ✏️ **Editar tiendas existentes**
- 🗑️ **Eliminar tiendas**
- 👥 **Gestión de usuarios** (activar/desactivar/cambiar roles)
- 📈 **Estadísticas del sistema**

## 🌐 Endpoints de la API

### **Autenticación:**
```
POST /api/users/register    - Registro de nuevos usuarios
POST /api/users/login       - Inicio de sesión
GET  /api/users/profile     - Perfil del usuario actual
GET  /api/users/verify-token - Verificar validez del token
GET  /api/users/            - Lista de usuarios (solo admin)
```

### **Tiendas:**
```
GET    /api/stores          - Listar tiendas (autenticado)
POST   /api/stores          - Crear tienda (solo admin)
GET    /api/stores/{id}     - Ver tienda específica (autenticado)
PUT    /api/stores/{id}     - Actualizar tienda (solo admin)
DELETE /api/stores/{id}     - Eliminar tienda (solo admin)
GET    /api/stores/stats    - Estadísticas (solo admin)
```

## 📂 Estructura de Archivos

```
api_store/
├── 🔧 Backend
│   ├── models/
│   │   ├── user_model.py       # Modelo de usuario con roles
│   │   └── store_model.py      # Modelo de tienda
│   ├── config/
│   │   ├── auth_config.py      # Configuración de autenticación
│   │   └── database.py         # Configuración de base de datos
│   ├── utils/
│   │   ├── auth_utils.py       # Utilidades JWT y hashing
│   │   └── auth_decorators.py  # Decoradores de protección
│   ├── repositories/
│   │   ├── user_repository.py  # CRUD de usuarios
│   │   └── store_repository.py # CRUD de tiendas
│   ├── services/
│   │   ├── user_service.py     # Lógica de negocio de usuarios
│   │   └── store_service.py    # Lógica de negocio de tiendas
│   └── controllers/
│       ├── user_controller.py  # Endpoints de usuarios
│       └── store_controller.py # Endpoints de tiendas
├── 🎨 Frontend
│   ├── templates/
│   │   └── index.html          # SPA con autenticación completa
│   └── static/
│       ├── script.js           # Lógica JavaScript completa
│       └── styles.css          # Estilos CSS modernos
└── 📄 Configuración
    ├── Main.py                 # Servidor Flask principal
    ├── create_admin.py         # Script para crear admin
    ├── requirements.txt        # Dependencias
    └── README.md              # Documentación completa
```

## 🔑 Credenciales por Defecto

**Usuario Administrador:**
- **Username:** `admin`
- **Email:** `admin@tiendas.com`
- **Password:** `admin123`
- **Role:** `admin`

## 🎯 Cómo Usar el Sistema

### **1. Iniciar el Servidor:**
```bash
cd api_store
python Main.py
```

### **2. Acceder a la Aplicación:**
- **URL:** http://localhost:5000
- **Registro:** Crear cuenta nueva desde la interfaz
- **Login:** Usar credenciales del admin o crear usuario nuevo

### **3. Funciones por Rol:**

**Usuario Regular:**
- Iniciar sesión y ver tiendas
- Navegar con paginación
- Ver detalles de cada tienda

**Administrador:**
- Todo lo anterior +
- Crear/editar/eliminar tiendas
- Gestionar usuarios del sistema
- Ver estadísticas globales

## 🛡️ Seguridad Implementada

### **Autenticación:**
- ✅ Tokens JWT con expiración (24 horas)
- ✅ Contraseñas hasheadas con bcrypt
- ✅ Validación de credenciales en login
- ✅ Verificación automática de tokens

### **Autorización:**
- ✅ Endpoints protegidos por decoradores
- ✅ Control de acceso basado en roles
- ✅ Validación de permisos en frontend
- ✅ Middleware de seguridad

### **Frontend:**
- ✅ Gestión automática de tokens
- ✅ Redirección en caso de sesión expirada
- ✅ UI adaptativa según permisos
- ✅ Validación de formularios

## 📊 Base de Datos

**Tablas:**
- **users** - Usuarios del sistema con roles y autenticación
- **stores** - 12,544 tiendas con datos completos

**Características:**
- SQLite para simplicidad
- Migraciones automáticas
- Datos de prueba incluidos
- Índices optimizados

## 🎨 Interfaz de Usuario

### **Características Visuales:**
- 🎨 **Diseño moderno** con Bootstrap 4.5.2
- 📱 **Responsive design** para móviles y tablets
- 🎯 **UX intuitiva** con navegación clara
- 🔔 **Notificaciones** en tiempo real
- ⚡ **Carga dinámica** sin refrescar página

### **Componentes:**
- **Navbar adaptativo** según autenticación
- **Formularios modales** para login/registro
- **Cards de tiendas** con información detallada
- **Paginación avanzada** con controles
- **Panel de administración** para gestión

## 🚀 Tecnologías Utilizadas

### **Backend:**
- **Flask 3.0.3** - Framework web
- **SQLAlchemy 2.0.30** - ORM
- **PyJWT 2.8.0** - Tokens JWT
- **bcrypt 4.0.1** - Hashing de contraseñas
- **python-jose 3.3.0** - Criptografía JWT

### **Frontend:**
- **HTML5/CSS3** - Estructura y estilos
- **JavaScript ES6+** - Lógica del cliente
- **jQuery 3.5.1** - Manipulación DOM
- **Bootstrap 4.5.2** - Framework CSS
- **Font Awesome 5.15.4** - Iconografía

## 📈 Próximas Mejoras

### **Posibles Extensiones:**
- 🔍 **Búsqueda avanzada** con filtros múltiples
- 📊 **Dashboard analítico** con gráficos
- 📧 **Sistema de notificaciones** por email
- 🔄 **API REST completa** con OpenAPI/Swagger
- 🔐 **OAuth 2.0** para login social
- 📱 **PWA** para uso offline

---

## 🎉 Sistema Completamente Funcional

El sistema está **100% operativo** con autenticación completa, gestión de roles, interfaz moderna y backend robusto. ¡Listo para usar en producción con las mejoras de seguridad necesarias!

**Estado:** ✅ **COMPLETADO**
**Fecha:** Septiembre 2025
**Desarrollador:** GitHub Copilot