from abc import ABC, abstractmethod

class NotificationStrategy(ABC):
    @abstractmethod
    def send(self, recipient, message):
        pass

class ConsoleStrategy(NotificationStrategy):
    def send(self, recipient, message):
        print(f"[NOTIFICACIÓN] Para: {recipient} - {message}")

class FileStrategy(NotificationStrategy):
    def __init__(self, filename='notifications.log'):
        self.filename = filename
    
    def send(self, recipient, message):
        with open(self.filename, 'a') as f:
            f.write(f"{recipient}: {message}\n")
