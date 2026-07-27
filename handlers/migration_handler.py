from database.models import SessionLocal, User, Product, Purchase, Setting, Tenant
from datetime import datetime

class MigrationHandler:
    @staticmethod
    def export_all_data():
        session = SessionLocal()
        data = {
            'users': [],
            'products': [],
            'purchases': [],
            'settings': {},
        }
        
        for u in session.query(User).all():
            data['users'].append({
                'telegram_id': u.telegram_id, 'username': u.username,
                'first_name': u.first_name, 'balance': u.balance,
                'total_purchases': u.total_purchases, 'total_spent': u.total_spent
            })
        
        for p in session.query(Product).all():
            data['products'].append({
                'name': p.name, 'description': p.description,
                'price': p.price, 'stock': p.stock, 'category': p.category
            })
        
        for s in session.query(Setting).all():
            data['settings'][s.key] = s.value
        
        session.close()
        return data
    
    @staticmethod
    def import_data(data):
        session = SessionLocal()
        
        for u_data in data.get('users', []):
            existing = session.query(User).filter_by(telegram_id=u_data['telegram_id']).first()
            if not existing:
                user = User(**u_data)
                session.add(user)
        
        for p_data in data.get('products', []):
            product = Product(**p_data)
            session.add(product)
        
        session.commit()
        session.close()
    
    @staticmethod
    def reset_database():
        from database.models import Base, engine
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        from database.models import init_db
        init_db()

migration_handler = MigrationHandler()
