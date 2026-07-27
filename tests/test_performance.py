import time
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import init_db
from database.db_manager import DBManager

class TestPerformance:
    @pytest.fixture(autouse=True)
    def setup(self):
        init_db()
        self.db = DBManager()
        yield
        self.db.close()
    
    def test_user_creation_speed(self):
        start = time.time()
        for i in range(100):
            self.db.get_user(900000 + i)
        elapsed = time.time() - start
        assert elapsed < 5.0, f"User creation too slow: {elapsed:.2f}s"
    
    def test_product_query_speed(self):
        start = time.time()
        for _ in range(100):
            self.db.get_products()
        elapsed = time.time() - start
        assert elapsed < 3.0, f"Product query too slow: {elapsed:.2f}s"
    
    def test_settings_read_speed(self):
        start = time.time()
        for _ in range(100):
            self.db.get_setting('welcome_text', '')
        elapsed = time.time() - start
        assert elapsed < 2.0, f"Settings read too slow: {elapsed:.2f}s"
    
    def test_settings_write_speed(self):
        start = time.time()
        for i in range(50):
            self.db.set_setting(f'perf_test_{i}', f'value_{i}')
        elapsed = time.time() - start
        assert elapsed < 3.0, f"Settings write too slow: {elapsed:.2f}s"
    
    def test_stats_speed(self):
        start = time.time()
        for _ in range(20):
            self.db.get_stats()
        elapsed = time.time() - start
        assert elapsed < 2.0, f"Stats query too slow: {elapsed:.2f}s"
    
    def test_balance_operations_speed(self):
        user = self.db.create_user(999990, 'perf_test', 'Perf')
        start = time.time()
        for i in range(50):
            self.db.add_balance(999990, 10)
            self.db.subtract_balance(999990, 5)
        elapsed = time.time() - start
        assert elapsed < 3.0, f"Balance ops too slow: {elapsed:.2f}s"
