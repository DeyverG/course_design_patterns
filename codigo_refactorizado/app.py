from flask import Flask
from flask_restful import Api
from endpoints import (
    AuthenticationResource,
    ProductsResource,
    CategoriesResource,
    FavoritesResource
)

# Aplicación Flask
app = Flask(__name__)
api = Api(app)

# Registrar los endpoints
api.add_resource(AuthenticationResource, '/auth')
api.add_resource(ProductsResource, '/products', '/products/<int:product_id>')
api.add_resource(CategoriesResource, '/categories', '/categories/<int:category_id>')
api.add_resource(FavoritesResource, '/favorites')

if __name__ == '__main__':
    app.run(debug=True)
