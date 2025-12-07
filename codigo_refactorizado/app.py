from flask import Flask
from flask_restful import Api
from endpoints import (
    AuthenticationResource,
    ProductsResource,
    CategoriesResource,
    FavoritesResource
)
from notifications.event_manager import EventManager
from notifications.subscribers.log_subscriber import LogSubscriber
from notifications.subscribers.recommendation_subscriber import RecommendationSubscriber

# Aplicación Flask
app = Flask(__name__)
api = Api(app)

# Configurar suscriptores
event_manager = EventManager()
event_manager.subscribe('ProductCreatedEvent', LogSubscriber())
event_manager.subscribe('FavoriteAddedEvent', LogSubscriber())
event_manager.subscribe('FavoriteAddedEvent', RecommendationSubscriber())

# Registrar los endpoints
api.add_resource(AuthenticationResource, '/auth')
api.add_resource(ProductsResource, '/products', '/products/<int:product_id>')
api.add_resource(CategoriesResource, '/categories', '/categories/<int:category_id>')
api.add_resource(FavoritesResource, '/favorites')

if __name__ == '__main__':
    app.run(debug=True)
