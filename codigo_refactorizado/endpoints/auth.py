from flask import request
from flask_restful import Resource
from config.settings import AUTH_USERNAME, AUTH_PASSWORD, VALID_TOKEN


class AuthenticationResource(Resource):
    """Recurso para autenticación de usuarios."""

    def post(self):
        """
        Autentica un usuario y retorna un token.
        
        Espera JSON con 'username' y 'password'.
        Retorna un token si las credenciales son válidas.
        """
        username = request.json.get('username')
        password = request.json.get('password')

        if username == AUTH_USERNAME and password == AUTH_PASSWORD:
            return {'token': VALID_TOKEN}, 200
        
        return {'message': 'Unauthorized: invalid credentials'}, 401
