from .base_repository import BaseRepository


class ProductRepository(BaseRepository):
    """Repositorio específico para productos."""
    
    COLLECTION_NAME = 'products'

    def get_by_category(self, category):
        """Obtiene productos filtrados por categoría."""
        products = self.get_all()
        return [p for p in products if p['category'].lower() == category.lower()]

    def create(self, name, category, price):
        """Crea un nuevo producto con ID automático."""
        new_product = {
            'id': self._generate_id(),
            'name': name,
            'category': category,
            'price': price
        }
        self.add(new_product)
        return new_product
