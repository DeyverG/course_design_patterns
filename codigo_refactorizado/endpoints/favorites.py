from flask_restful import Resource, reqparse
from utils.database_connection import DatabaseConnection
from utils.auth_decorator import require_auth
from repositories.favorite_repository import FavoriteRepository
from config.settings import DATABASE_FILE
from notifications.event_manager import EventManager
from notifications.events.favorite_events import FavoriteAddedEvent


class FavoritesResource(Resource):
    """Recurso REST para operaciones con favoritos."""

    def __init__(self):
        db = DatabaseConnection(DATABASE_FILE)
        self.repository = FavoriteRepository(db)
        self.event_manager = EventManager()
        
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user_id', type=int, required=True, help='User ID')
        self.parser.add_argument('product_id', type=int, required=True, help='Product ID')

    @require_auth
    def get(self):
        """Obtiene todos los favoritos."""
        return self.repository.get_all(), 200

    @require_auth
    def post(self):
        """Agrega un producto a favoritos."""
        args = self.parser.parse_args()
        
        new_favorite = self.repository.create(
            user_id=args['user_id'],
            product_id=args['product_id']
        )
        
        event = FavoriteAddedEvent(new_favorite)
        self.event_manager.emit(event)
        
        return {
            'message': 'Product added to favorites',
            'favorite': new_favorite
        }, 201

    @require_auth
    def delete(self):
        """Elimina un producto de favoritos."""
        args = self.parser.parse_args()
        
        self.repository.remove(args['user_id'], args['product_id'])
        
        return {'message': 'Product removed from favorites'}, 200
