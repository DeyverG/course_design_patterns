from abc import ABC


class BaseRepository(ABC):
    """
    Clase base para repositorios.
    
    Cada repositorio hijo solo necesita definir:
    - COLLECTION_NAME: nombre de la colección en el JSON
    """

    # Cada repositorio define su colección
    COLLECTION_NAME = None

    def __init__(self, db_connection):
        """Recibe la conexión a BD (inyección de dependencias)."""
        self.db = db_connection

    def get_all(self):
        """Obtiene todos los elementos de la colección."""
        return self.db.get_collection(self.COLLECTION_NAME)

    def _save_all(self, items):
        """Guarda todos los elementos de la colección."""
        self.db.save_collection(self.COLLECTION_NAME, items)

    def get_by_id(self, item_id):
        """Obtiene un elemento por su ID."""
        items = self.get_all()
        return next((item for item in items if item.get('id') == item_id), None)

    def add(self, item):
        """Agrega un nuevo elemento."""
        items = self.get_all()
        items.append(item)
        self._save_all(items)

    def _generate_id(self):
        """Genera un nuevo ID basado en el máximo existente."""
        items = self.get_all()
        if not items:
            return 1
        return max(item.get('id', 0) for item in items) + 1
