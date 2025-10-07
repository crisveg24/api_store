# 🚀 Resumen: Migración SQLite → Railway (PostgreSQL)

## ✅ Archivos en carpeta `railway/`

Esta carpeta contiene toda la configuración necesaria para desplegar en Railway:

### 📝 Archivos de Configuración

1. **`Procfile`** - Comando de inicio para Railway
   ```
   web: gunicorn Main:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120
   ```

2. **`railway.json`** - Configuración de build y deploy
   - Builder: NIXPACKS
   - Auto-restart en caso de fallo
   - 10 reintentos máximos

3. **`.env.example`** - Plantilla de variables de entorno
   - ⚠️ Solo valores de ejemplo
   - Debes crear tu propio `.env` con valores reales
   - NUNCA subir `.env` real a Git

4. **`DEPLOYMENT.md`** - Guía completa de despliegue
   - Pasos detallados
   - Troubleshooting
   - Comandos útiles

5. **`README.md`** - Este archivo

## 🎯 Cómo Usar

### Para Railway (Producción)

1. **Copia `Procfile` y `railway.json` a la raíz:**
   ```bash
   cp railway/Procfile .
   cp railway/railway.json .
   ```

2. **Configura variables en Railway Dashboard:**
   - NO uses los valores de `.env.example`
   - Genera claves únicas para cada variable
   - Railway creará `DATABASE_URL` automáticamente

3. **Push a GitHub:**
   ```bash
   git push origin Development
   ```

4. **Railway despliega automáticamente**

### Para Desarrollo Local

1. **Copia `.env.example` a la raíz:**
   ```bash
   cp railway/.env.example .env
   ```

2. **Edita `.env` con tus valores locales:**
   - Cambia todas las claves
   - Configura tu BD local (o déjalo para SQLite)

3. **Ejecuta normalmente:**
   ```bash
   python Main.py
   ```

## 🔐 Seguridad Implementada

### ✅ Lo que está SEGURO
- Todas las claves en variables de entorno
- `.env` está en `.gitignore`
- Solo plantillas de ejemplo en Git
- Sin contraseñas hardcodeadas

### ❌ NUNCA hagas esto
- Subir archivo `.env` con valores reales
- Hardcodear contraseñas en código
- Usar claves de ejemplo en producción
- Compartir claves en documentación

### 🔑 Generar Claves Seguras

**Python:**
```python
import secrets
print(secrets.token_hex(32))
```

**OpenSSL (Linux/Mac):**
```bash
openssl rand -hex 32
```

**PowerShell (Windows):**
```powershell
[System.Convert]::ToBase64String((1..32|%{Get-Random -Max 256}))
```

## 📊 Diferencias por Entorno

| Aspecto | Desarrollo Local | Railway Producción |
|---------|-----------------|-------------------|
| Base de datos | SQLite (default) | PostgreSQL (auto) |
| Variables | Archivo `.env` | Railway Dashboard |
| Puerto | 5000 | `$PORT` (dinámico) |
| Workers | 1 (debug) | 4 (gunicorn) |
| HTTPS | No | Sí (automático) |
| Dominio | localhost | `*.up.railway.app` |

## 🛠️ Archivos Relacionados Modificados

### `config/database.py`
Ahora soporta múltiples bases de datos con prioridad:
1. `DATABASE_URL` (Railway)
2. Variables individuales (`PGUSER`, etc.)
3. SQLite (fallback)

### `requirements.txt`
Agregadas dependencias de producción:
- `psycopg2-binary` - Driver PostgreSQL
- `gunicorn` - Servidor WSGI

## 📁 Estructura del Proyecto

```
api_store/
├── railway/               ← Nueva carpeta organizada
│   ├── .env.example      ← Plantilla (segura para Git)
│   ├── Procfile          ← Comando de inicio
│   ├── railway.json      ← Configuración Railway
│   ├── DEPLOYMENT.md     ← Guía detallada
│   └── README.md         ← Este archivo
├── config/
│   └── database.py       ← Modificado para multi-DB
├── requirements.txt      ← Actualizado con psycopg2, gunicorn
├── Main.py              ← Sin cambios (lee variables de .env)
├── .env                 ← NO en Git (creas tú)
├── .env.example         ← BORRAR (ahora está en railway/)
├── .gitignore           ← Ya configurado correctamente
└── ...
```

## 🔄 Flujo de Trabajo

### Desarrollo Local
```bash
# 1. Clonar repo
git clone <repo>

# 2. Crear .env desde plantilla
cp railway/.env.example .env

# 3. Editar .env con valores locales

# 4. Instalar y ejecutar
pip install -r requirements.txt
python Main.py
```

### Desplegar a Railway
```bash
# 1. Copiar archivos necesarios a raíz
cp railway/Procfile .
cp railway/railway.json .

# 2. Commit y push
git add .
git commit -m "Deploy to Railway"
git push origin Development

# 3. Configurar variables en Railway Dashboard
# (ver railway/DEPLOYMENT.md)
```

## 📚 Documentación Adicional

- **`DEPLOYMENT.md`** - Guía paso a paso para Railway
- **Raíz del proyecto** - Archivos operacionales
- **Esta carpeta** - Solo configuración y documentación

## ⚠️ Recordatorios de Seguridad

1. ✅ `.env` está en `.gitignore`
2. ✅ Solo `.env.example` (sin valores reales) en Git
3. ✅ Variables sensibles solo en Railway Dashboard
4. ✅ Sin contraseñas hardcodeadas en código
5. ✅ Claves generadas aleatoriamente

## 🎉 Beneficios de esta Organización

- 📁 Archivos de configuración en un solo lugar
- 🔐 Separación clara entre plantillas y valores reales
- 📖 Documentación centralizada
- 🚀 Fácil de mantener y actualizar
- 🔒 Seguridad por diseño
