from database.db_manager import DBManager
class GiftService:
    def __init__(self): self.db=DBManager()
    def create(self,v): return self.db.create_gift(v)
    def redeem(self,c,uid): return self.db.redeem_gift(c.upper(),uid)
    def close(self): self.db.close()
