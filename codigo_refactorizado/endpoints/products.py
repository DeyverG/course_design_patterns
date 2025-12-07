from flask import request
from flask_restful import Resource, reqparse
from utils.database_connection import DatabaseConnection
from utils.auth_decorator import require_auth
from repositories.product_repository import ProductRepository
from config.settings import DATABASE_FILE
from notifications.event_manager import EventManager
from notifications.events.product_events import ProductCreatedEvent


class ProductsResource(Resource):
    """Recurso REST para operaciones con productos."""

    def __init__(self):
        # Inyección de dependencias a través del repositorio
        db = DatabaseConnection(DATABASE_FILE)
        self.repository = ProductRepository(db)
        self.event_manager = EventManager()
        
        # Parser para validar datos de entrada
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=True, help='Name of the product')
        self.parser.add_argument('category', type=str, required=True, help='Category of the product')
        self.parser.add_argument('price', type=float, required=True, help='Price of the product')

    @require_auth  # Decorador que maneja la autenticación
    def get(self, product_id=None):
        """
        Obtiene productos.
        
        - Sin parámetros: retorna todos los productos
        - Con product_id: retorna un producto específico
        - Con ?category=X: filtra por categoría
        """
        category_filter = request.args.get('category')

        # Filtrar por categoría si se especifica
        if category_filter:
            return self.repository.get_by_category(category_filter)
        
        # Buscar producto específico por ID
        if product_id is not None:
            product = self.repository.get_by_id(product_id)
            if product:
                return product
            return {'message': 'Product not found'}, 404
        
        # Retornar todos los productos
        return self.repository.get_all()

    @require_auth
    def post(self):
        """Crea un nuevo producto."""
        args = self.parser.parse_args()
        
        new_product = self.repository.create(
            name=args['name'],
            category=args['category'],
            price=args['price']
        )
        
        event = ProductCreatedEvent(new_product)
        self.event_manager.emit(event)
        
        return {'message': 'Product added', 'product': new_product}, 201
