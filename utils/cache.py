from datetime import datetime, timedelta

class Cache:
    def __init__(self, ttl_minutes=5):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return value
            del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())
    
    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        self.cache.clear()
    
    def get_or_set(self, key, callback):
        value = self.get(key)
        if value is None:
            value = callback()
            self.set(key, value)
        return value
    
    def size(self):
        return len(self.cache)
    
    def keys(self):
        return list(self.cache.keys())

user_cache = Cache(ttl_minutes=5)
product_cache = Cache(ttl_minutes=10)
setting_cache = Cache(ttl_minutes=30)
