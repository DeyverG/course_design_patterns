from .base_event import BaseEvent

class ProductCreatedEvent(BaseEvent):
    def __init__(self, product):
        super().__init__({
            'product_id': product['id'],
            'product_name': product['name'],
            'category': product['category'],
            'price': product['price']
        })

class ProductPriceChangedEvent(BaseEvent):
    def __init__(self, product_id, old_price, new_price):
        super().__init__({
            'product_id': product_id,
            'old_price': old_price,
            'new_price': new_price,
            'change_percentage': ((new_price - old_price) / old_price) * 100
        })

class ProductDeletedEvent(BaseEvent):
    def __init__(self, product_id, product_name):
        super().__init__({
            'product_id': product_id,
            'product_name': product_name
        })
