import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import (
    init_db, SessionLocal, User, Product, Purchase, 
    PixRecharge, GiftCard, Login, Setting, Alert, 
    Log, Tenant, Cart, Coupon, FAQ, Ranking
)
from datetime import datetime

class TestModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.session = SessionLocal()
    
    def test_user_model(self):
        user = User(telegram_id=999, first_name='Test', balance=100)
        self.assertEqual(user.telegram_id, 999)
        self.assertEqual(user.balance, 100)
    
    def test_product_model(self):
        product = Product(name='Test', price=50, stock=10)
        self.assertEqual(product.name, 'Test')
        self.assertEqual(product.price, 50)
        self.assertEqual(product.stock, 10)
    
    def test_purchase_model(self):
        purchase = Purchase(
            user_id=1, product_name='Test', amount=50,
            email='test@test.com', password='pass',
            purchase_date=datetime.now()
        )
        self.assertEqual(purchase.amount, 50)
    
    def test_pix_recharge_model(self):
        pix = PixRecharge(
            user_id=1, amount=100, pix_id='test123',
            status='pending', expires_at=datetime.now()
        )
        self.assertEqual(pix.amount, 100)
        self.assertEqual(pix.status, 'pending')
    
    def test_gift_card_model(self):
        gift = GiftCard(code='TEST123', value=50)
        self.assertEqual(gift.code, 'TEST123')
        self.assertEqual(gift.value, 50)
    
    def test_login_model(self):
        login = Login(
            service_name='Netflix', email='test@test.com',
            password='pass123', price=15
        )
        self.assertEqual(login.service_name, 'Netflix')
    
    def test_setting_model(self):
        setting = Setting(tenant_id=1, key='test', value='value')
        self.assertEqual(setting.key, 'test')
        self.assertEqual(setting.value, 'value')
    
    def test_alert_model(self):
        alert = Alert(user_id=1, product_id=1, active=True)
        self.assertTrue(alert.active)
    
    def test_tenant_model(self):
        tenant = Tenant(name='TestStore', status='active', plan='pro')
        self.assertEqual(tenant.name, 'TestStore')
        self.assertEqual(tenant.plan, 'pro')
    
    def test_cart_model(self):
        cart = Cart(user_id=1, product_id=1, quantity=2)
        self.assertEqual(cart.quantity, 2)
    
    def test_coupon_model(self):
        coupon = Coupon(code='PROMO10', discount_percent=10, max_uses=100)
        self.assertEqual(coupon.code, 'PROMO10')
        self.assertEqual(coupon.discount_percent, 10)
    
    def test_faq_model(self):
        faq = FAQ(question='Test?', answer='Answer', position=1)
        self.assertEqual(faq.question, 'Test?')
    
    def test_ranking_model(self):
        ranking = Ranking(user_id=1, category='buyer', position=1, value=100)
        self.assertEqual(ranking.position, 1)

if __name__ == '__main__':
    unittest.main()
