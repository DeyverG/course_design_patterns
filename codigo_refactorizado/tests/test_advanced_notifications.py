import pytest
import sys
import json
from notifications.event_manager import EventManager
from notifications.subscribers.console_subscriber import ConsoleSubscriber
from notifications.subscribers.log_subscriber import LogSubscriber
from notifications.events.base_event import BaseEvent

class SimpleEvent(BaseEvent):
    def __init__(self, message):
        super().__init__({'message': message})

@pytest.fixture
def event_manager():
    # Reset singleton
    EventManager._instance = None
    return EventManager()

def test_console_subscriber_output(capsys):
    subscriber = ConsoleSubscriber()
    event = SimpleEvent("Hello World")
    
    subscriber.handle(event)
    
    captured = capsys.readouterr()
    assert "[LIVE DEMO] Event Received: SimpleEvent" in captured.out
    assert '"message": "Hello World"' in captured.out

def test_event_manager_no_subscribers(event_manager):
    # Should not raise any exception
    event = SimpleEvent("No one listening")
    event_manager.emit(event)

def test_multiple_subscribers_same_event(event_manager, capsys):
    console_sub = ConsoleSubscriber()
    
    # Mock another subscriber
    class CounterSubscriber:
        def __init__(self):
            self.count = 0
        def handle(self, event):
            self.count += 1
            
    counter_sub = CounterSubscriber()
    
    event_manager.subscribe('SimpleEvent', console_sub)
    event_manager.subscribe('SimpleEvent', counter_sub)
    
    event = SimpleEvent("Broadcast")
    event_manager.emit(event)
    
    # Check console output
    captured = capsys.readouterr()
    assert "Event Received: SimpleEvent" in captured.out
    
    # Check counter
    assert counter_sub.count == 1

def test_subscriber_multiple_events(event_manager, tmp_path):
    log_file = tmp_path / "multi_event.log"
    subscriber = LogSubscriber(log_file=str(log_file))
    
    event_manager.subscribe('SimpleEvent', subscriber)
    event_manager.subscribe('OtherEvent', subscriber)
    
    event1 = SimpleEvent("First")
    
    class OtherEvent(BaseEvent):
        def __init__(self, val):
            super().__init__({'val': val})
            
    event2 = OtherEvent(123)
    
    event_manager.emit(event1)
    event_manager.emit(event2)
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 2
        assert 'SimpleEvent' in lines[0]
        assert 'OtherEvent' in lines[1]
