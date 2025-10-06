# Configuración de JWT
import os
from datetime import timedelta

# Clave secreta para firmar los tokens JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tu-clave-secreta-para-jwt-en-produccion-debe-ser-muy-segura")

# Ubicación donde buscar el token JWT (en headers)
JWT_TOKEN_LOCATION = ["headers"]

# Tiempo de expiración del token de acceso (24 horas)
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

# Nombre del header donde se espera el token
JWT_HEADER_NAME = "Authorization"

# Tipo de token (Bearer)
JWT_HEADER_TYPE = "Bearer"

# Configuraciones adicionales para la API de stores
JWT_ERROR_MESSAGE_KEY = "message"
JWT_BLACKLIST_ENABLED = False
JWT_BLACKLIST_TOKEN_CHECKS = ["access"]