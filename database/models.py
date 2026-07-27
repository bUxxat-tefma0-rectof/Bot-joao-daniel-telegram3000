from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

db_url = os.environ.get('DATABASE_URL', 'sqlite:///database/bot.db')
if not db_url.startswith('sqlite'): db_url = 'sqlite:///database/bot.db'
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Tenant(Base):
    __tablename__ = 'tenants'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    bot_token = Column(String, unique=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    mp_access_token = Column(String)
    status = Column(String, default='active')
    plan = Column(String, default='free')
    expiration_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), default=1)
    telegram_id = Column(Integer, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    balance = Column(Float, default=0.0)
    commission_balance = Column(Float, default=0.0)
    whatsapp = Column(String)
    referral_code = Column(String)
    referred_by = Column(Integer, ForeignKey('users.id'))
    total_referrals = Column(Integer, default=0)
    total_purchases = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    total_recharged = Column(Float, default=0.0)
    gifts_redeemed = Column(Integer, default=0)
    affiliate_points = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)
    is_owner = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    flood_count = Column(Integer, default=0)
    flood_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    purchases = relationship('Purchase', back_populates='user')
    recharges = relationship('PixRecharge', back_populates='user')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), default=1)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category = Column(String, default='')
    image = Column(String)
    warranty = Column(String)
    active = Column(Boolean, default=True)
    total_sold = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    position = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    tenant_id = Column(Integer, default=1)
    product_name = Column(String)
    amount = Column(Float)
    email = Column(String)
    password = Column(String)
    activation_link = Column(String)
    duration = Column(String)
    expiration_date = Column(DateTime)
    purchase_date = Column(DateTime, default=datetime.now)
    status = Column(String, default='active')
    purchase_id = Column(String, unique=True)
    user = relationship('User', back_populates='purchases')

class PixRecharge(Base):
    __tablename__ = 'pix_recharges'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    tenant_id = Column(Integer, default=1)
    amount = Column(Float, nullable=False)
    pix_id = Column(String, unique=True)
    qr_code = Column(Text)
    copy_paste = Column(Text)
    status = Column(String, default='pending')
    expires_at = Column(DateTime)
    paid_at = Column(DateTime)
    bonus_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    user = relationship('User', back_populates='recharges')

class GiftCard(Base):
    __tablename__ = 'gift_cards'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, default=1)
    code = Column(String, unique=True)
    value = Column(Float)
    is_used = Column(Boolean, default=False)
    used_by = Column(Integer)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    used_at = Column(DateTime)

class Login(Base):
    __tablename__ = 'logins'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, default=1)
    service_name = Column(String, nullable=False)
    email = Column(String)
    password = Column(String)
    description = Column(Text)
    duration = Column(String)
    price = Column(Float)
    is_sold = Column(Boolean, default=False)
    sold_to = Column(Integer)
    purchase_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    sold_at = Column(DateTime)

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, default=1)
    key = Column(String, nullable=False)
    value = Column(Text)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    product_id = Column(Integer)
    active = Column(Boolean, default=True)

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, default=1)
    log_type = Column(String)
    user_id = Column(Integer)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class Ranking(Base):
    __tablename__ = 'rankings'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, default=1)
    user_id = Column(Integer)
    category = Column(String)
    position = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)
    value = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

class Cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    product_id = Column(Integer)
    quantity = Column(Integer, default=1)

class Coupon(Base):
    __tablename__ = 'coupons'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, default=1)
    code = Column(String, unique=True)
    discount_percent = Column(Float)
    max_uses = Column(Integer)
    used_count = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

class FAQ(Base):
    __tablename__ = 'faqs'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, default=1)
    question = Column(Text)
    answer = Column(Text)
    position = Column(Integer, default=0)

def init_db():
    os.makedirs('database', exist_ok=True)
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if not db.query(Tenant).filter_by(id=1).first():
            db.add(Tenant(id=1, name='Store', status='active', plan='enterprise'))
        defaults = {
            'welcome_text': '', 'welcome_image': '', 'support_link': '', 'support_text': '',
            'about_text': '', 'terms_text': '', 'recarga_text': '', 'pix_ask_text': '',
            'pix_result_text': '', 'catalog_text': '', 'product_text': '', 'insufficient_text': '',
            'expired_pix_text': '', 'profile_text': '', 'stock_text': '', 'ranking_text': '',
            'multi_text': '', 'convert_text': '', 'success_text': '', 'flood_text': '',
            'history_text': '', 'gift_text': '', 'faq_text': '',
            'btn1_text': '', 'btn2_text': '', 'btn3_text': '', 'btn4_text': '',
            'btn5_text': '', 'btn6_text': '', 'btn7_text': '', 'btn8_text': '',
            'btn1_pos': 'full', 'btn2_pos': 'left', 'btn3_pos': 'right',
            'btn4_pos': 'full', 'btn5_pos': 'left', 'btn6_pos': 'right',
            'btn7_pos': 'left', 'btn8_pos': 'right',
            'buy_btn': '', 'multi_btn': '', 'add_saldo_btn': '', 'pix_btn': '',
            'cancel_btn': '', 'back_text': '', 'history_btn': '', 'convert_btn': '',
            'wait_btn': '', 'copy_btn': '', 'pix_auto_btn': '', 'rank_balance_btn': '',
            'rank_recharge_btn': '', 'rank_products_btn': '', 'rank_recent_btn': '',
            'pix_expiration': '15', 'deposit_min': '2', 'deposit_max': '150',
            'bonus_percentage': '0', 'bonus_min_value': '10', 'commission_percentage': '10',
            'affiliate_system': 'on', 'affiliate_points_per_recharge': '1',
            'affiliate_min_points': '500', 'affiliate_multiplier': '0.01',
            'maintenance_mode': 'off', 'registration_bonus': '0',
            'bot_version': '1.0.0', 'separator': '===', 'flood_seconds': '6',
            'convert_seconds': '80',
        }
        for k, v in defaults.items():
            if not db.query(Setting).filter_by(tenant_id=1, key=k).first():
                db.add(Setting(tenant_id=1, key=k, value=v))
        db.commit()
    except: db.rollback()
    finally: db.close()
