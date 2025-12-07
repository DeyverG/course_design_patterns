from .base_subscriber import BaseSubscriber
import json

class RecommendationSubscriber(BaseSubscriber):
    def __init__(self, recommendation_file='recommendations.json'):
        self.recommendation_file = recommendation_file
    
    def handle(self, event):
        # Simula alimentar un sistema de recomendaciones
        # En un caso real, esto podría llamar a un servicio de ML o actualizar una tabla de pesos
        data = event.data
        entry = {
            'user_id': data['user_id'],
            'interaction': 'add_favorite',
            'product_id': data['product_id'],
            'timestamp': event.timestamp.isoformat()
        }
        
        # Por ahora, solo lo guardamos en un archivo JSON simulando el "sistema"
        try:
            with open(self.recommendation_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"Error updating recommendation system: {e}")
