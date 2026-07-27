import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import init_db, SessionLocal, User, Product, Purchase, PixRecharge, Setting
from database.db_manager import DBManager

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.db = DBManager()
    
    def test_create_user(self):
        user = self.db.create_user(123456, 'testuser', 'Test')
        self.assertIsNotNone(user)
        self.assertEqual(user.telegram_id, 123456)
        self.assertEqual(user.first_name, 'Test')
    
    def test_get_user(self):
        user = self.db.get_user(123456)
        self.assertIsNotNone(user)
    
    def test_balance(self):
        self.db.add_balance(123456, 50)
        bal = self.db.get_balance(123456)
        self.assertEqual(bal, 50)
    
    def test_subtract_balance(self):
        result = self.db.subtract_balance(123456, 20)
        self.assertTrue(result)
        bal = self.db.get_balance(123456)
        self.assertEqual(bal, 30)
    
    def test_insufficient_balance(self):
        result = self.db.subtract_balance(123456, 1000)
        self.assertFalse(result)
    
    def test_add_product(self):
        p = self.db.add_product('Test Product', 10, 50, 'Test', 'Description')
        self.assertIsNotNone(p)
        self.assertEqual(p.name, 'Test Product')
        self.assertEqual(p.price, 10)
    
    def test_get_products(self):
        products = self.db.get_products()
        self.assertGreater(len(products), 0)
    
    def test_get_product(self):
        p = self.db.get_product(1)
        self.assertIsNotNone(p)
    
    def test_decrease_stock(self):
        result = self.db.decrease_stock(1)
        self.assertTrue(result)
    
    def test_settings(self):
        self.db.set_setting('test_key', 'test_value')
        val = self.db.get_setting('test_key')
        self.assertEqual(val, 'test_value')
    
    def test_get_all_settings(self):
        settings = self.db.get_all_settings()
        self.assertIsInstance(settings, dict)
    
    def test_create_purchase(self):
        p = self.db.create_purchase(123456, 'Test Product', 10, 'test@test.com', 'pass123')
        self.assertIsNotNone(p)
        self.assertEqual(p.product_name, 'Test Product')
    
    def test_get_user_purchases(self):
        purchases = self.db.get_user_purchases(123456)
        self.assertIsInstance(purchases, list)
    
    def test_stats(self):
        stats = self.db.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('users', stats)
    
    def test_get_top_products(self):
        products = self.db.get_top_products(5)
        self.assertIsInstance(products, list)
    
    def test_get_top_buyers(self):
        buyers = self.db.get_top_buyers(5)
        self.assertIsInstance(buyers, list)
    
    def test_get_top_rechargers(self):
        rechargers = self.db.get_top_rechargers(5)
        self.assertIsInstance(rechargers, list)
    
    def test_get_top_balance(self):
        users = self.db.get_top_balance(5)
        self.assertIsInstance(users, list)
    
    def test_gift_card(self):
        g = self.db.create_gift(50)
        self.assertIsNotNone(g)
        self.assertEqual(g.value, 50)
    
    def test_redeem_gift(self):
        g = self.db.create_gift(100)
        result = self.db.redeem_gift(g.code, 123456)
        self.assertTrue(result)
    
    def test_add_login(self):
        l = self.db.add_login('Netflix', 'test@test.com', 'pass123')
        self.assertIsNotNone(l)
    
    def test_get_available_login(self):
        l = self.db.get_available_login('Netflix')
        self.assertIsNotNone(l)
    
    def test_stock_count(self):
        count = self.db.get_stock_count()
        self.assertIsInstance(count, int)
    
    def test_check_flood(self):
        result = self.db.check_flood(123456)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
