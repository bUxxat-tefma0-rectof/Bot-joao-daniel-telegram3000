from database.db_manager import DBManager
from database.models import SessionLocal, Tenant, Setting

class TenantHandler:
    def __init__(self):
        self.db = DBManager()
    
    def get_tenant(self, tenant_id):
        session = SessionLocal()
        tenant = session.query(Tenant).filter_by(id=tenant_id).first()
        session.close()
        return tenant
    
    def create_tenant(self, name, owner_id, plan='free'):
        import uuid
        session = SessionLocal()
        tenant = Tenant(
            name=name,
            bot_token=f"BOT_{uuid.uuid4().hex}",
            owner_id=owner_id,
            status='active',
            plan=plan
        )
        session.add(tenant)
        session.commit()
        session.refresh(tenant)
        
        defaults = {
            'welcome_text': '', 'support_link': '', 'btn1_text': '🛍️ Comprar',
            'btn2_text': '👤 Perfil', 'btn3_text': '💰 Recarregar', 'btn4_text': '💼 Afiliado',
            'btn1_pos': 'full', 'btn2_pos': 'left', 'btn3_pos': 'right', 'btn4_pos': 'full',
        }
        for k, v in defaults.items():
            session.add(Setting(tenant_id=tenant.id, key=k, value=v))
        
        session.commit()
        session.close()
        return tenant
    
    def update_tenant(self, tenant_id, **kwargs):
        session = SessionLocal()
        tenant = session.query(Tenant).filter_by(id=tenant_id).first()
        if tenant:
            for k, v in kwargs.items():
                if hasattr(tenant, k):
                    setattr(tenant, k, v)
            session.commit()
        session.close()
    
    def delete_tenant(self, tenant_id):
        session = SessionLocal()
        session.query(Tenant).filter_by(id=tenant_id).delete()
        session.commit()
        session.close()
    
    def get_all_tenants(self):
        session = SessionLocal()
        tenants = session.query(Tenant).all()
        session.close()
        return tenants
    
    def suspend_tenant(self, tenant_id):
        self.update_tenant(tenant_id, status='suspended')
    
    def activate_tenant(self, tenant_id):
        self.update_tenant(tenant_id, status='active')
    
    def renew_tenant(self, tenant_id, days=30):
        from datetime import datetime, timedelta
        new_exp = datetime.now() + timedelta(days=days)
        self.update_tenant(tenant_id, expiration_date=new_exp)

tenant_handler = TenantHandler()
