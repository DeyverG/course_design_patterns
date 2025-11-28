"""
Decorador para autenticación de endpoints.
"""

from functools import wraps
from flask import request
from config.settings import VALID_TOKEN, ERROR_MESSAGES


def is_valid_token(token):
    """Valida si el token es correcto."""
    return token == VALID_TOKEN


def require_auth(func):
    """
    Decorador que verifica la autenticación antes de ejecutar el endpoint.
    
    Uso:
        @require_auth
        def get(self):
            # Este código solo se ejecuta si el token es válido
            return {'data': 'protected data'}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return {'message': ERROR_MESSAGES['token_not_found']}, 401
        
        if not is_valid_token(token):
            return {'message': ERROR_MESSAGES['invalid_token']}, 401
        
        # Si el token es válido, ejecuta la función original
        return func(*args, **kwargs)
    
    return wrapper
