import asyncio
from database.db_manager import DBManager
from services.pix_service import PixService
from services.affiliate_service import AffiliateService
from services.login_service import LoginService

db = DBManager()

class PaymentChecker:
    def __init__(self, bot):
        self.bot = bot
        self.checking = {}
    
    async def start_checking(self, user_id, pix_id, product_id=None, quantity=1):
        self.checking[pix_id] = {'user_id': user_id, 'product_id': product_id, 'quantity': quantity, 'checks': 0}
        await self.check_loop(pix_id)
    
    async def check_loop(self, pix_id):
        ps = PixService()
        max_checks = 60
        while pix_id in self.checking and self.checking[pix_id]['checks'] < max_checks:
            await asyncio.sleep(10)
            self.checking[pix_id]['checks'] += 1
            result = ps.verificar(pix_id)
            if result.get('aprovado'):
                success, total = db.confirm_pix(pix_id)
                if success:
                    user_id = self.checking[pix_id]['user_id']
                    af = AffiliateService(); af.add_commission(user_id, total); af.close()
                    product_id = self.checking[pix_id]['product_id']
                    if product_id:
                        p = db.get_product(product_id)
                        if p:
                            qty = self.checking[pix_id]['quantity']
                            total_price = p.price * qty
                            if db.get_balance(user_id) >= total_price:
                                ls = LoginService()
                                for _ in range(qty):
                                    db.subtract_balance(user_id, p.price)
                                    db.decrease_stock(product_id)
                                    login = ls.get(p.name)
                                    email = login.email if login else ''
                                    pw = login.password if login else ''
                                    if login: ls.sold(login.id, user_id)
                                    db.create_purchase(user_id, p.name, p.price, email, pw, '')
                                ls.close()
                    try: await self.bot.send_message(user_id, f"✅ Pagamento aprovado!\n💰 R$ {total:.2f}")
                    except: pass
                    del self.checking[pix_id]
                    break
        ps.close()
        if pix_id in self.checking: del self.checking[pix_id]

payment_checker = None
