from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db_manager import DBManager
from database.models import SessionLocal, PixRecharge, Purchase
from datetime import datetime

class Scheduler:
    def __init__(self, bot=None): self.scheduler=AsyncIOScheduler(); self.bot=bot; self.db=DBManager()
    def start(self):
        self.scheduler.add_job(self.check_pix,'interval',minutes=1)
        self.scheduler.add_job(self.check_purchases,'interval',hours=6)
        self.scheduler.start()
    async def check_pix(self):
        db=SessionLocal()
        expired=db.query(PixRecharge).filter(PixRecharge.status=='pending',PixRecharge.expires_at<datetime.now()).all()
        for p in expired:
            p.status='expired'
            if self.bot:
                try:
                    txt=self.db.get_setting('expired_pix_text','PIX Expirado')
                    await self.bot.send_message(p.user_id,txt.replace('{valor}',f'R$ {p.amount:.2f}').replace('{id}',p.pix_id))
                except: pass
        db.commit(); db.close()
    async def check_purchases(self):
        db=SessionLocal()
        expired=db.query(Purchase).filter(Purchase.expiration_date<datetime.now(),Purchase.status=='active').all()
        for p in expired: p.status='expired'
        db.commit(); db.close()
    def stop(self): self.scheduler.shutdown()
