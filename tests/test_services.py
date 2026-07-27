import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gift_service import GiftService
from services.login_service import LoginService
from services.affiliate_service import AffiliateService

class TestGiftService(unittest.TestCase):
    def setUp(self):
        self.gs = GiftService()
    
    def test_create_gift(self):
        gift = self.gs.create(50)
        self.assertIsNotNone(gift)
        self.assertEqual(gift.value, 50)
    
    def test_redeem_gift(self):
        gift = self.gs.create(100)
        result = self.gs.redeem(gift.code, 123456)
        self.assertTrue(result)
    
    def tearDown(self):
        self.gs.close()

class TestLoginService(unittest.TestCase):
    def setUp(self):
        self.ls = LoginService()
    
    def test_add_login(self):
        login = self.ls.add('Netflix', 'test@test.com', 'pass', 'desc', '30 dias', 15)
        self.assertIsNotNone(login)
    
    def test_get_available_login(self):
        login = self.ls.get('Netflix')
        self.assertIsNotNone(login)
    
    def test_stock_count(self):
        count = self.ls.count()
        self.assertIsInstance(count, int)
    
    def tearDown(self):
        self.ls.close()

class TestAffiliateService(unittest.TestCase):
    def setUp(self):
        self.af = AffiliateService()
    
    def test_add_commission(self):
        self.af.add_commission(123456, 50)
    
    def tearDown(self):
        self.af.close()

if __name__ == '__main__':
    unittest.main()
