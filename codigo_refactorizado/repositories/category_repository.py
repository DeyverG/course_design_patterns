from .base_repository import BaseRepository


class CategoryRepository(BaseRepository):
    """Repositorio específico para categorías."""
    
    COLLECTION_NAME = 'categories'

    def get_by_name(self, name):
        """Obtiene una categoría por nombre."""
        categories = self.get_all()
        return next((c for c in categories if c['name'] == name), None)

    def exists(self, name):
        """Verifica si una categoría existe."""
        return self.get_by_name(name) is not None

    def create(self, name):
        """Crea una nueva categoría con ID automático."""
        new_category = {
            'id': self._generate_id(),
            'name': name
        }
        self.add(new_category)
        return new_category

    def remove(self, name):
        """Elimina una categoría por nombre."""
        categories = self.get_all()
        updated = [c for c in categories if c['name'] != name]
        self._save_all(updated)
