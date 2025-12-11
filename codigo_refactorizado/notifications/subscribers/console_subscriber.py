from .base_subscriber import BaseSubscriber
import json

class ConsoleSubscriber(BaseSubscriber):
    def handle(self, event):
        event_name = type(event).__name__
        print(f"\n[LIVE DEMO] Event Received: {event_name}")
        print(f"[LIVE DEMO] Data: {json.dumps(event.data, indent=2)}\n")
