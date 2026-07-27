from utils.cache import Cache
from database.db_manager import DBManager

user_cache = Cache(ttl_minutes=5)
product_cache = Cache(ttl_minutes=10)
setting_cache = Cache(ttl_minutes=30)
stats_cache = Cache(ttl_minutes=15)

class CacheHandler:
    @staticmethod
    def get_user(telegram_id):
        def fetch():
            db = DBManager()
            user = db.get_user(telegram_id)
            db.close()
            return user
        
        return user_cache.get_or_set(f'user_{telegram_id}', fetch)
    
    @staticmethod
    def get_product(product_id):
        def fetch():
            db = DBManager()
            product = db.get_product(product_id)
            db.close()
            return product
        
        return product_cache.get_or_set(f'product_{product_id}', fetch)
    
    @staticmethod
    def get_setting(key, default=''):
        def fetch():
            db = DBManager()
            value = db.get_setting(key, default)
            db.close()
            return value
        
        return setting_cache.get_or_set(f'setting_{key}', fetch)
    
    @staticmethod
    def get_stats():
        def fetch():
            db = DBManager()
            stats = db.get_stats()
            db.close()
            return stats
        
        return stats_cache.get_or_set('stats', fetch)
    
    @staticmethod
    def clear_user_cache(telegram_id):
        user_cache.delete(f'user_{telegram_id}')
    
    @staticmethod
    def clear_product_cache(product_id):
        product_cache.delete(f'product_{product_id}')
    
    @staticmethod
    def clear_setting_cache(key):
        setting_cache.delete(f'setting_{key}')
    
    @staticmethod
    def clear_all():
        user_cache.clear()
        product_cache.clear()
        setting_cache.clear()
        stats_cache.clear()

cache_handler = CacheHandler()
