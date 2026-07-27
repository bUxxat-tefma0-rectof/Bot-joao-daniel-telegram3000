from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db_manager import DBManager
from database.models import SessionLocal, PixRecharge, Purchase, Coupon
from datetime import datetime, timedelta
import asyncio

class SchedulerHandler:
    def __init__(self, bot=None):
        self.bot = bot
        self.db = DBManager()
        self.scheduler = None
    
    def start_all_jobs(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        self.scheduler = AsyncIOScheduler(event_loop=loop)
        self.scheduler.add_job(self.check_expired_pix, 'interval', minutes=1)
        self.scheduler.add_job(self.check_expired_purchases, 'interval', hours=6)
        self.scheduler.add_job(self.clean_old_logs, 'interval', hours=24)
        self.scheduler.start()
    
    async def check_expired_pix(self):
        session = SessionLocal()
        expired = session.query(PixRecharge).filter(
            PixRecharge.status == 'pending',
            PixRecharge.expires_at < datetime.now()
        ).all()
        for p in expired:
            p.status = 'expired'
            if self.bot:
                try:
                    txt = self.db.get_setting('expired_pix_text', 'PIX Expirado')
                    await self.bot.send_message(p.user_id, txt.replace('{valor}', f'R$ {p.amount:.2f}'))
                except: pass
        session.commit()
        session.close()
    
    async def check_expired_purchases(self):
        session = SessionLocal()
        expired = session.query(Purchase).filter(
            Purchase.expiration_date < datetime.now(),
            Purchase.status == 'active'
        ).all()
        for p in expired: p.status = 'expired'
        session.commit()
        session.close()
    
    async def clean_old_logs(self):
        from utils.logger import logger
        logger.clean_old_logs(30)

scheduler_handler = None
