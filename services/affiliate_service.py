from database.db_manager import DBManager
class AffiliateService:
    def __init__(self): self.db=DBManager()
    def add_commission(self,uid,amt):
        u=self.db.get_user(uid)
        if u and u.referred_by:
            ref=self.db.get_user(u.referred_by)
            if ref:
                pct=float(self.db.get_setting('commission_percentage','10'))
                val=amt*(pct/100); ref.commission_balance+=val; ref.total_referrals+=1
                pts=int(self.db.get_setting('affiliate_points_per_recharge','1'))
                u.affiliate_points+=pts; self.db.db.commit()
    def close(self): self.db.close()
