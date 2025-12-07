from datetime import datetime

class BaseEvent:
    def __init__(self, data=None):
        self.timestamp = datetime.now()
        self.data = data or {}
    
    def to_dict(self):
        return {
            'event_type': type(self).__name__,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data
        }
