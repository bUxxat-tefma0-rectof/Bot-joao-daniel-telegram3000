from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db_manager import DBManager
from database.models import SessionLocal, PixRecharge, Purchase, GiftCard, Coupon
from datetime import datetime, timedelta

class SchedulerHandler:
    def __init__(self, bot=None):
        self.scheduler = AsyncIOScheduler()
        self.bot = bot
        self.db = DBManager()
    
    def start_all_jobs(self):
        self.scheduler.add_job(self.check_expired_pix, 'interval', minutes=1, id='pix_check')
        self.scheduler.add_job(self.check_expired_purchases, 'interval', hours=6, id='purchase_check')
        self.scheduler.add_job(self.check_expired_coupons, 'interval', hours=1, id='coupon_check')
        self.scheduler.add_job(self.clean_old_logs, 'interval', hours=24, id='log_clean')
        self.scheduler.add_job(self.optimize_database, 'interval', hours=12, id='db_optimize')
        self.scheduler.add_job(self.send_daily_report, 'cron', hour=23, minute=59, id='daily_report')
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
                    txt = self.db.get_setting('expired_pix_text', '⌛️ PIX Expirado')
                    await self.bot.send_message(
                        p.user_id,
                        txt.replace('{valor}', f'R$ {p.amount:.2f}').replace('{id}', p.pix_id)
                    )
                except:
                    pass
        
        session.commit()
        session.close()
    
    async def check_expired_purchases(self):
        session = SessionLocal()
        expired = session.query(Purchase).filter(
            Purchase.expiration_date < datetime.now(),
            Purchase.status == 'active'
        ).all()
        
        for p in expired:
            p.status = 'expired'
        
        session.commit()
        session.close()
    
    async def check_expired_coupons(self):
        session = SessionLocal()
        expired = session.query(Coupon).filter(
            Coupon.active == True,
            Coupon.expires_at < datetime.now()
        ).all()
        
        for c in expired:
            c.active = False
        
        session.commit()
        session.close()
    
    async def clean_old_logs(self):
        from utils.logger import logger
        logger.clean_old_logs(30)
    
    async def optimize_database(self):
        from utils.database_utils import db_utils
        db_utils.optimize_database()
    
    async def send_daily_report(self):
        if not self.bot:
            return
        
        from config.settings import ADMIN_ID
        stats = self.db.get_stats()
        
        txt = f"📊 *Relatório Diário*\n\n"
        txt += f"👥 Usuários: {stats['users']}\n"
        txt += f"🛒 Vendas hoje: {stats['today_sales']}\n"
        txt += f"💰 Receita hoje: R$ {stats['today_revenue']:.2f}\n"
        txt += f"💳 Recargas: {stats['total_recharges']}\n"
        txt += f"📦 Estoque: {stats['logins_stock']}"
        
        try:
            await self.bot.send_message(ADMIN_ID, txt, parse_mode='Markdown')
        except:
            pass
    
    def stop_all(self):
        self.scheduler.shutdown()

scheduler_handler = None
