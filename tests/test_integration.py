import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import init_db
from database.db_manager import DBManager
from services.pix_service import PixService
from services.gift_service import GiftService
from services.login_service import LoginService
from services.affiliate_service import AffiliateService

class TestIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        init_db()
        self.db = DBManager()
        self.user = self.db.create_user(777777, 'integration_test', 'Integration')
        yield
        self.db.close()
    
    def test_full_purchase_flow(self):
        self.db.add_balance(777777, 100)
        product = self.db.add_product('Integration Product', 50, 10, 'Test')
        
        bal_before = self.db.get_balance(777777)
        assert bal_before == 100
        
        result = self.db.subtract_balance(777777, product.price)
        assert result == True
        
        self.db.decrease_stock(product.id)
        
        ls = LoginService()
        login = ls.get(product.name)
        email = login.email if login else 'test@test.com'
        pw = login.password if login else 'pass123'
        if login: ls.sold(login.id, 777777)
        
        purchase = self.db.create_purchase(777777, product.name, product.price, email, pw, '')
        ls.close()
        
        assert purchase is not None
        assert purchase.product_name == product.name
        
        bal_after = self.db.get_balance(777777)
        assert bal_after == 50
        
        product_after = self.db.get_product(product.id)
        assert product_after.stock == 9
    
    def test_recharge_flow(self):
        initial_bal = self.db.get_balance(777777)
        self.db.add_balance(777777, 200)
        new_bal = self.db.get_balance(777777)
        assert new_bal == initial_bal + 200
    
    def test_gift_card_flow(self):
        gs = GiftService()
        gift = gs.create(500)
        assert gift is not None
        
        bal_before = self.db.get_balance(777777)
        result = gs.redeem(gift.code, 777777)
        assert result == True
        
        bal_after = self.db.get_balance(777777)
        assert bal_after == bal_before + 500
        gs.close()
    
    def test_affiliate_flow(self):
        referred = self.db.create_user(777778, 'referred', 'Referred')
        referrer = self.db.get_user(777777)
        referred.referred_by = 777777
        
        af = AffiliateService()
        af.add_commission(referred.telegram_id, 100)
        af.close()
        
        referrer_after = self.db.get_user(777777)
        assert referrer_after.commission_balance > 0 or referrer_after.total_referrals > 0
    
    def test_stock_management(self):
        ls = LoginService()
        initial_count = ls.count()
        
        ls.add('TestService', 'test@test.com', 'pass', '', '30 dias', 10)
        ls.add('TestService', 'test2@test.com', 'pass2', '', '30 dias', 10)
        
        after_add = ls.count()
        assert after_add == initial_count + 2
        
        login = ls.get('TestService')
        assert login is not None
        
        ls.sold(login.id, 777777)
        after_sold = ls.count()
        assert after_sold == initial_count + 1
        
        ls.close()
