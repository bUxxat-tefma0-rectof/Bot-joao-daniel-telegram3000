from database.db_manager import DBManager
from database.models import SessionLocal, Tenant
from datetime import datetime, timedelta

db = DBManager()

class SubscriptionHandler:
    PLANS = {
        'free': {'name': 'Grátis', 'price': 0, 'max_users': 100, 'max_products': 10},
        'basic': {'name': 'Básico', 'price': 29.90, 'max_users': 500, 'max_products': 50},
        'pro': {'name': 'Profissional', 'price': 79.90, 'max_users': 2000, 'max_products': 200},
        'enterprise': {'name': 'Enterprise', 'price': 199.90, 'max_users': 10000, 'max_products': 1000},
    }
    
    @classmethod
    def get_plan(cls, plan_name):
        return cls.PLANS.get(plan_name, cls.PLANS['free'])
    
    @classmethod
    def upgrade_plan(cls, tenant_id, new_plan):
        session = SessionLocal()
        tenant = session.query(Tenant).filter_by(id=tenant_id).first()
        if tenant:
            tenant.plan = new_plan
            if new_plan == 'free':
                tenant.expiration_date = None
            else:
                tenant.expiration_date = datetime.now() + timedelta(days=30)
            session.commit()
        session.close()
    
    @classmethod
    def check_expiration(cls, tenant_id):
        session = SessionLocal()
        tenant = session.query(Tenant).filter_by(id=tenant_id).first()
        if tenant and tenant.expiration_date:
            if tenant.expiration_date < datetime.now():
                tenant.status = 'expired'
                session.commit()
        session.close()
    
    @classmethod
    def get_remaining_days(cls, tenant_id):
        session = SessionLocal()
        tenant = session.query(Tenant).filter_by(id=tenant_id).first()
        if tenant and tenant.expiration_date:
            remaining = (tenant.expiration_date - datetime.now()).days
            session.close()
            return max(0, remaining)
        session.close()
        return 0

subscription_handler = SubscriptionHandler()
