import pytest
import os
import json
from notifications.event_manager import EventManager
from notifications.events.product_events import ProductCreatedEvent
from notifications.events.favorite_events import FavoriteAddedEvent
from notifications.subscribers.log_subscriber import LogSubscriber
from notifications.subscribers.recommendation_subscriber import RecommendationSubscriber
from notifications.subscribers.base_subscriber import BaseSubscriber
from notifications.strategies.notification_strategy import ConsoleStrategy, FileStrategy

class MockSubscriber(BaseSubscriber):
    def __init__(self):
        self.handled_events = []

    def handle(self, event):
        self.handled_events.append(event)

@pytest.fixture
def event_manager():
    # Reset singleton for testing
    EventManager._instance = None
    return EventManager()

def test_singleton_pattern(event_manager):
    em1 = EventManager()
    em2 = EventManager()
    assert em1 is em2

def test_subscribe_and_emit(event_manager):
    subscriber = MockSubscriber()
    event_manager.subscribe('ProductCreatedEvent', subscriber)
    
    product_data = {'id': 1, 'name': 'Test Product', 'category': 'Test', 'price': 100}
    event = ProductCreatedEvent(product_data)
    
    event_manager.emit(event)
    
    assert len(subscriber.handled_events) == 1
    assert subscriber.handled_events[0] == event

def test_unsubscribe(event_manager):
    subscriber = MockSubscriber()
    event_manager.subscribe('ProductCreatedEvent', subscriber)
    event_manager.unsubscribe('ProductCreatedEvent', subscriber)
    
    product_data = {'id': 1, 'name': 'Test Product', 'category': 'Test', 'price': 100}
    event = ProductCreatedEvent(product_data)
    
    event_manager.emit(event)
    
    assert len(subscriber.handled_events) == 0

def test_log_subscriber(tmp_path):
    log_file = tmp_path / "test_audit.log"
    subscriber = LogSubscriber(log_file=str(log_file))
    
    product_data = {'id': 1, 'name': 'Test Product', 'category': 'Test', 'price': 100}
    event = ProductCreatedEvent(product_data)
    
    subscriber.handle(event)
    
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        content = f.read()
        log_entry = json.loads(content)
        assert log_entry['event_type'] == 'ProductCreatedEvent'
        assert log_entry['data']['product_name'] == 'Test Product'

def test_favorite_added_event_and_recommendation_subscriber(tmp_path):
    rec_file = tmp_path / "test_recommendations.json"
    subscriber = RecommendationSubscriber(recommendation_file=str(rec_file))
    
    favorite_data = {'user_id': 123, 'product_id': 456}
    event = FavoriteAddedEvent(favorite_data)
    
    subscriber.handle(event)
    
    assert os.path.exists(rec_file)
    with open(rec_file, 'r') as f:
        content = f.read()
        entry = json.loads(content)
        assert entry['user_id'] == 123
        assert entry['product_id'] == 456
        assert entry['interaction'] == 'add_favorite'

def test_strategies(capsys, tmp_path):
    # Test ConsoleStrategy
    console_strategy = ConsoleStrategy()
    console_strategy.send("user@example.com", "Hello Console")
    captured = capsys.readouterr()
    assert "[NOTIFICACIÓN] Para: user@example.com - Hello Console" in captured.out

    # Test FileStrategy
    log_file = tmp_path / "test_strategy.log"
    file_strategy = FileStrategy(filename=str(log_file))
    file_strategy.send("user@example.com", "Hello File")
    
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        content = f.read()
        assert "user@example.com: Hello File" in content
