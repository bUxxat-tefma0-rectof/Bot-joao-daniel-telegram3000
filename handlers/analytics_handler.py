from database.db_manager import DBManager
from database.models import SessionLocal, Purchase, PixRecharge, User
from datetime import datetime, timedelta

db = DBManager()

class AnalyticsHandler:
    @staticmethod
    def get_daily_revenue(days=7):
        session = SessionLocal()
        data = []
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            sales = session.query(Purchase).filter(
                Purchase.purchase_date >= date,
                Purchase.purchase_date < date + timedelta(days=1)
            ).all()
            total = sum(s.amount for s in sales)
            data.append({'date': date.strftime('%d/%m'), 'revenue': total})
        session.close()
        return reversed(data)
    
    @staticmethod
    def get_weekly_stats():
        session = SessionLocal()
        week_ago = datetime.now() - timedelta(days=7)
        
        new_users = session.query(User).filter(User.created_at >= week_ago).count()
        sales = session.query(Purchase).filter(Purchase.purchase_date >= week_ago).all()
        recharges = session.query(PixRecharge).filter(
            PixRecharge.created_at >= week_ago,
            PixRecharge.status == 'completed'
        ).all()
        
        stats = {
            'new_users': new_users,
            'total_sales': len(sales),
            'total_revenue': sum(s.amount for s in sales),
            'total_recharges': len(recharges),
            'total_recharge_amount': sum(r.amount for r in recharges),
        }
        session.close()
        return stats
    
    @staticmethod
    def get_monthly_stats():
        session = SessionLocal()
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        
        stats = {
            'users': session.query(User).filter(User.created_at >= month_start).count(),
            'sales': session.query(Purchase).filter(Purchase.purchase_date >= month_start).count(),
            'revenue': sum(p.amount for p in session.query(Purchase).filter(Purchase.purchase_date >= month_start).all()),
            'avg_ticket': 0
        }
        
        if stats['sales'] > 0:
            stats['avg_ticket'] = stats['revenue'] / stats['sales']
        
        session.close()
        return stats
    
    @staticmethod
    def get_conversion_rate():
        session = SessionLocal()
        total_users = session.query(User).count()
        buyers = session.query(User).filter(User.total_purchases > 0).count()
        session.close()
        return (buyers / total_users * 100) if total_users > 0 else 0

analytics_handler = AnalyticsHandler()
