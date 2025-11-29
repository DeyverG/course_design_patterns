from flask_restful import Resource, reqparse
from utils.database_connection import DatabaseConnection
from utils.auth_decorator import require_auth
from repositories.category_repository import CategoryRepository
from config.settings import DATABASE_FILE


class CategoriesResource(Resource):
    """Recurso REST para operaciones con categorías."""

    def __init__(self):
        db = DatabaseConnection(DATABASE_FILE)
        self.repository = CategoryRepository(db)
        
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=True, help='Name of the category')

    @require_auth
    def get(self, category_id=None):
        """
        Obtiene categorías.
        
        - Sin parámetros: retorna todas las categorías
        - Con category_id: retorna una categoría específica
        """
        if category_id is not None:
            category = self.repository.get_by_id(category_id)
            if category:
                return category
            return {'message': 'Category not found'}, 404
        
        return self.repository.get_all()

    @require_auth
    def post(self):
        """Crea una nueva categoría."""
        args = self.parser.parse_args()
        category_name = args['name']

        # Validar que no exista
        if self.repository.exists(category_name):
            return {'message': 'Category already exists'}, 400

        new_category = self.repository.create(category_name)
        return {'message': 'Category added successfully', 'category': new_category}, 201

    @require_auth
    def delete(self):
        """Elimina una categoría por nombre."""
        args = self.parser.parse_args()
        category_name = args['name']

        # Validar que exista
        if not self.repository.exists(category_name):
            return {'message': 'Category not found'}, 404

        self.repository.remove(category_name)
        return {'message': 'Category removed successfully'}, 200
