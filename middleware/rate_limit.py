from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_limited(self, user_id, max_requests=10, window_seconds=60):
        now = datetime.now()
        window = now - timedelta(seconds=window_seconds)
        
        self.requests[user_id] = [t for t in self.requests[user_id] if t > window]
        
        if len(self.requests[user_id]) >= max_requests:
            return True
        
        self.requests[user_id].append(now)
        return False
    
    def get_remaining(self, user_id, max_requests=10):
        now = datetime.now()
        window = now - timedelta(seconds=60)
        self.requests[user_id] = [t for t in self.requests[user_id] if t > window]
        return max_requests - len(self.requests[user_id])
    
    def reset(self, user_id):
        if user_id in self.requests:
            del self.requests[user_id]

rate_limiter = RateLimiter()
