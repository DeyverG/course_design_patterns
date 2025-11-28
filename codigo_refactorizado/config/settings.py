"""
Módulo de configuración centralizada.
"""

# Configuración de la base de datos
DATABASE_FILE = 'db.json'
FAVORITES_FILE = 'favorites.json'

# Configuración de autenticación
VALID_TOKEN = 'abcd1234'
AUTH_USERNAME = 'student'
AUTH_PASSWORD = 'desingp'

# Mensajes de error (centralizados para consistencia)
ERROR_MESSAGES = {
    'token_not_found': 'Unauthorized: access token not found',
    'invalid_token': 'Unauthorized: invalid token',
    'not_found': '{resource} not found',
    'already_exists': '{resource} already exists',
    'required_field': '{field} is required',
}
