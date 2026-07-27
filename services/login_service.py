from database.db_manager import DBManager
class LoginService:
    def __init__(self): self.db=DBManager()
    def add(self,s,e,p,d='',du='30 dias',pr=0): return self.db.add_login(s,e,p,d,du,pr)
    def get(self,s): return self.db.get_available_login(s)
    def sold(self,lid,uid): self.db.mark_login_sold(lid,uid)
    def clear(self): return self.db.clear_stock()
    def remove(self,s): return self.db.remove_by_platform(s)
    def update_price(self,s,pr): return self.db.update_price_by_service(s,pr)
    def update_all(self,pr): return self.db.update_all_prices(pr)
    def count(self): return self.db.get_stock_count()
    def close(self): self.db.close()
