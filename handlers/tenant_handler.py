from database.models import SessionLocal, Tenant, Setting

class TenantHandler:
    def __init__(self): pass
    
    def get_tenant(self, tenant_id):
        session = SessionLocal()
        tenant = session.query(Tenant).filter_by(id=tenant_id).first()
        session.close()
        return tenant
    
    def create_tenant(self, name, owner_id, plan='free'):
        import uuid
        session = SessionLocal()
        tenant = Tenant(name=name, bot_token=f"BOT_{uuid.uuid4().hex}", owner_id=owner_id, status='active', plan=plan)
        session.add(tenant)
        session.commit()
        session.close()
        return tenant
    
    def update_tenant(self, tenant_id, **kwargs):
        session = SessionLocal()
        tenant = session.query(Tenant).filter_by(id=tenant_id).first()
        if tenant:
            for k, v in kwargs.items():
                if hasattr(tenant, k): setattr(tenant, k, v)
            session.commit()
        session.close()
    
    def get_all_tenants(self):
        session = SessionLocal()
        tenants = session.query(Tenant).all()
        session.close()
        return tenants

tenant_handler = TenantHandler()
