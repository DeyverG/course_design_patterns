from abc import ABC, abstractmethod

class BaseSubscriber(ABC):
    @abstractmethod
    def handle(self, event):
        pass
