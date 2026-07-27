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

class CacheHandler:
    def __init__(self):
        self.user_cache = Cache(ttl_minutes=5)
        self.product_cache = Cache(ttl_minutes=10)
        self.setting_cache = Cache(ttl_minutes=30)
        self.stats_cache = Cache(ttl_minutes=15)
    
    def get_user(self, telegram_id):
        from database.db_manager import DBManager
        def fetch():
            db = DBManager()
            user = db.get_user(telegram_id)
            db.close()
            return user
        return self.user_cache.get_or_set(f'user_{telegram_id}', fetch)
    
    def get_product(self, product_id):
        from database.db_manager import DBManager
        def fetch():
            db = DBManager()
            product = db.get_product(product_id)
            db.close()
            return product
        return self.product_cache.get_or_set(f'product_{product_id}', fetch)
    
    def get_setting(self, key, default=''):
        from database.db_manager import DBManager
        def fetch():
            db = DBManager()
            value = db.get_setting(key, default)
            db.close()
            return value
        return self.setting_cache.get_or_set(f'setting_{key}', fetch)
    
    def get_stats(self):
        from database.db_manager import DBManager
        def fetch():
            db = DBManager()
            stats = db.get_stats()
            db.close()
            return stats
        return self.stats_cache.get_or_set('stats', fetch)
    
    def clear_all(self):
        self.user_cache.clear()
        self.product_cache.clear()
        self.setting_cache.clear()
        self.stats_cache.clear()

cache_handler = CacheHandler()
