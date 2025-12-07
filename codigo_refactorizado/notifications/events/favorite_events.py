from .base_event import BaseEvent

class FavoriteAddedEvent(BaseEvent):
    def __init__(self, favorite):
        super().__init__({
            'user_id': favorite['user_id'],
            'product_id': favorite['product_id']
        })
