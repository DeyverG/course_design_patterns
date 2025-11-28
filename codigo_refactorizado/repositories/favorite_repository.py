from .base_repository import BaseRepository


class FavoriteRepository(BaseRepository):
    """Repositorio específico para favoritos."""
    
    COLLECTION_NAME = 'favorites'

    def get_by_user(self, user_id):
        """Obtiene todos los favoritos de un usuario."""
        favorites = self.get_all()
        return [f for f in favorites if f['user_id'] == user_id]

    def create(self, user_id, product_id):
        """Agrega un producto a favoritos."""
        new_favorite = {
            'user_id': user_id,
            'product_id': product_id
        }
        self.add(new_favorite)
        return new_favorite

    def remove(self, user_id, product_id):
        """Elimina un favorito específico."""
        favorites = self.get_all()
        updated = [
            f for f in favorites
            if not (f['user_id'] == user_id and f['product_id'] == product_id)
        ]
        self._save_all(updated)
