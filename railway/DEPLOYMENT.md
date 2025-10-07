# 🚂 Guía de Despliegue en Railway

## 📋 Prerrequisitos

1. Cuenta en [Railway.app](https://railway.app/)
2. Repositorio Git con el código
3. PostgreSQL habilitado en Railway

## 🚀 Pasos para Desplegar

### 1. Crear Proyecto en Railway

1. Ve a [Railway.app](https://railway.app/)
2. Click en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway y selecciona `api_store`

### 2. Agregar Base de Datos PostgreSQL

1. En tu proyecto, click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway creará automáticamente `DATABASE_URL`

### 3. Configurar Variables de Entorno

En Railway → Tu servicio → **Variables**, agrega:

```env
# ⚠️ IMPORTANTE: Genera claves únicas y seguras
JWT_SECRET_KEY=<genera-una-clave-aleatoria-segura>
SECRET_KEY=<genera-otra-clave-diferente>

# Configuración de entorno
FLASK_ENV=production
DEBUG=False
```

**🔐 Cómo generar claves seguras:**
```python
# En Python:
import secrets
print(secrets.token_hex(32))
```

O en terminal:
```bash
# Linux/Mac:
openssl rand -hex 32

# PowerShell:
[System.Convert]::ToBase64String((1..32|%{Get-Random -Max 256}))
```

### 4. Railway Detecta Automáticamente

- ✅ `requirements.txt` - Instala dependencias
- ✅ `Procfile` - Comando de inicio
- ✅ `railway.json` - Configuración adicional

### 5. Desplegar

Railway desplegará automáticamente al hacer push a GitHub.

## 🔗 Acceder a tu Aplicación

Railway te dará una URL como:
```
https://tu-proyecto-production.up.railway.app
```

## 📊 Endpoints de la API

- `GET /` - Interfaz web
- `GET /api` - Información de la API
- `GET /health` - Health check
- `POST /api/users/login` - Login
- `GET /api/stores` - Listar tiendas

## 🛠️ Desarrollo Local

### Con SQLite (recomendado para desarrollo)
```bash
pip install -r requirements.txt
python Main.py
```

### Con PostgreSQL Local
```bash
# 1. Crear base de datos
psql -U postgres -c "CREATE DATABASE storesdb;"

# 2. Crear archivo .env (ver railway/.env.example)
cp railway/.env.example .env

# 3. Editar .env con tus credenciales locales

# 4. Ejecutar
pip install -r requirements.txt
python Main.py
```

## 🔄 Actualizar la Aplicación

```bash
git add .
git commit -m "Descripción de cambios"
git push origin Development
```

Railway redesplegará automáticamente.

## 🐛 Troubleshooting

### Ver Logs
Railway Dashboard → Tu servicio → Deployments → View Logs

### Error: "Application failed to start"
- Verifica `Procfile` en la raíz del proyecto
- Revisa que todas las dependencias estén en `requirements.txt`

### Error: "Database connection failed"
- Verifica que PostgreSQL esté agregado al proyecto
- Asegúrate de que `DATABASE_URL` esté en las variables

### Error: "Module not found"
- Verifica imports en el código
- Asegúrate de que `psycopg2-binary` esté en requirements.txt

## 🔐 Seguridad

### ✅ Variables en Railway (seguras)
- `JWT_SECRET_KEY`
- `SECRET_KEY`
- `DATABASE_URL` (generada automáticamente)

### ❌ NUNCA subir a Git
- Archivos `.env` con valores reales
- Contraseñas en código
- Claves API reales

### ✅ SÍ subir a Git
- `railway/.env.example` (plantilla sin valores)
- `Procfile`
- `railway.json`
- Documentación

## 📝 Notas Importantes

1. **DATABASE_URL**: Railway la genera automáticamente
2. **Puerto**: Railway asigna `$PORT` automáticamente
3. **HTTPS**: Incluido por defecto en Railway
4. **Dominio**: Puedes configurar uno personalizado

## 🎓 Credenciales por Defecto

Usuario administrador inicial:
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ Cámbialo después del primer login**

## 📚 Recursos

- [Railway Docs](https://docs.railway.app/)
- [Flask Deployment](https://flask.palletsprojects.com/en/latest/deploying/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

## 💡 Consejos

1. Usa variables de entorno para TODO lo sensible
2. Nunca hardcodees contraseñas o claves
3. Revisa logs regularmente
4. Configura monitoreo de errores
5. Implementa backups de la BD
