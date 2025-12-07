from .base_subscriber import BaseSubscriber
import json
from datetime import datetime

class LogSubscriber(BaseSubscriber):
    def __init__(self, log_file='audit.log'):
        self.log_file = log_file
    
    def handle(self, event):
        log_entry = {
            'logged_at': datetime.now().isoformat(),
            **event.to_dict()
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
