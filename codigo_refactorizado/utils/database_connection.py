import json


class DatabaseConnection:
    """
    Clase Singleton para manejar la conexión a la base de datos JSON.
    
    Solo proporciona operaciones genéricas de lectura/escritura.
    """
    
    _instances = {}

    def __new__(cls, json_file_path):
        """
        Controla la creación de instancias.
        Retorna la instancia existente o crea una nueva.
        """
        if json_file_path not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instances[json_file_path] = instance
        return cls._instances[json_file_path]

    def __init__(self, json_file_path):
        if self._initialized:
            return
            
        self.json_file_path = json_file_path
        self.data = None
        self._initialized = True
        self._connect()

    def _connect(self):
        """Carga los datos del archivo JSON."""
        try:
            with open(self.json_file_path, 'r') as json_file:
                self.data = json.load(json_file)
        except FileNotFoundError:
            self.data = {}
            self._save()

    def _save(self):
        """Guarda los datos en el archivo JSON."""
        with open(self.json_file_path, 'w') as json_file:
            json.dump(self.data, json_file, indent=4)

    # ============ Operaciones Genéricas ============
    
    def get_collection(self, collection_name):
        """
        Obtiene una colección por nombre.
        
        Args:
            collection_name: Nombre de la colección ('products', 'categories', etc.)
        
        Returns:
            Lista de elementos de la colección.
        """
        return self.data.get(collection_name, [])

    def save_collection(self, collection_name, items):
        """
        Guarda una colección completa.
        
        Args:
            collection_name: Nombre de la colección.
            items: Lista de elementos a guardar.
        """
        self.data[collection_name] = items
        self._save()
