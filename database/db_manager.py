from sqlalchemy.orm import Session
from database.models import SessionLocal, Tenant, User, Product, Purchase, PixRecharge, GiftCard, Login, Setting, Alert, Log, Ranking, Cart, Coupon, FAQ
from datetime import datetime, timedelta
import random, string, uuid

class DBManager:
    def __init__(self, tenant_id=1):
        self.db = SessionLocal()
        self.tenant_id = tenant_id
    
    def close(self): self.db.close()
    
    def get_setting(self, key, default=''):
        s = self.db.query(Setting).filter_by(tenant_id=self.tenant_id, key=key).first()
        return s.value if s else default
    
    def set_setting(self, key, value):
        s = self.db.query(Setting).filter_by(tenant_id=self.tenant_id, key=key).first()
        if s:
            s.value = str(value)
        else:
            self.db.add(Setting(tenant_id=self.tenant_id, key=key, value=str(value)))
        self.db.commit()
    
    def get_all_settings(self):
        return {s.key: s.value for s in self.db.query(Setting).filter_by(tenant_id=self.tenant_id).all()}
    
    def get_user(self, telegram_id):
        return self.db.query(User).filter_by(tenant_id=self.tenant_id, telegram_id=telegram_id).first()
    
    def create_user(self, telegram_id, username, first_name):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        bonus = float(self.get_setting('registration_bonus', '0'))
        u = User(
            tenant_id=self.tenant_id, telegram_id=telegram_id,
            username=username, first_name=first_name,
            referral_code=code, balance=bonus
        )
        self.db.add(u)
        self.db.commit()
        self.db.refresh(u)
        return u
    
    def get_balance(self, tid):
        u = self.get_user(tid)
        return u.balance if u else 0.0
    
    def add_balance(self, tid, amt):
        u = self.get_user(tid)
        if u:
            u.balance += amt
            u.total_recharged += amt
            self.db.commit()
    
    def subtract_balance(self, tid, amt):
        u = self.get_user(tid)
        if u and u.balance >= amt:
            u.balance -= amt
            u.total_spent += amt
            u.total_purchases += 1
            self.db.commit()
            return True
        return False
    
    def get_products(self, cat=None):
        q = self.db.query(Product).filter_by(tenant_id=self.tenant_id, active=True)
        if cat:
            q = q.filter_by(category=cat)
        return q.order_by(Product.position).all()
    
    def get_product(self, pid):
        return self.db.query(Product).filter_by(tenant_id=self.tenant_id, id=pid).first()
    
    def add_product(self, name, price, stock, cat='', desc=''):
        p = Product(
            tenant_id=self.tenant_id, name=name, price=float(price),
            stock=int(stock), category=cat, description=desc
        )
        self.db.add(p)
        self.db.commit()
        return p
    
    def delete_product(self, pid):
        p = self.get_product(pid)
        if p:
            p.active = False
            self.db.commit()
    
    def decrease_stock(self, pid):
        p = self.get_product(pid)
        if p and p.stock > 0:
            p.stock -= 1
            p.total_sold += 1
            self.db.commit()
            return True
        return False
    
    def create_purchase(self, uid, pname, amt, email='', pw='', link=''):
        pid = str(uuid.uuid4())
        p = Purchase(
            user_id=uid, tenant_id=self.tenant_id, product_name=pname,
            amount=amt, email=email, password=pw, activation_link=link,
            purchase_id=pid, expiration_date=datetime.now() + timedelta(days=30)
        )
        self.db.add(p)
        self.db.commit()
        return p
    
    def get_user_purchases(self, uid):
        return self.db.query(Purchase).filter_by(user_id=uid).order_by(Purchase.purchase_date.desc()).all()
    
    def get_purchase_by_id(self, pid):
        return self.db.query(Purchase).filter_by(purchase_id=pid).first()
    
    def create_pix(self, uid, amt, pix_id, qr, cp, exp):
        p = PixRecharge(
            tenant_id=self.tenant_id, user_id=uid, amount=amt,
            pix_id=pix_id, qr_code=qr, copy_paste=cp, expires_at=exp
        )
        self.db.add(p)
        self.db.commit()
        return p
    
    def confirm_pix(self, pix_id):
        p = self.db.query(PixRecharge).filter_by(pix_id=pix_id, status='pending').first()
        if p:
            p.status = 'completed'
            p.paid_at = datetime.now()
            bp = float(self.get_setting('bonus_percentage', '0'))
            bm = float(self.get_setting('bonus_min_value', '10'))
            bonus = p.amount * (bp / 100) if p.amount >= bm and bp > 0 else 0
            p.bonus_amount = bonus
            total = p.amount + bonus
            u = self.get_user(p.user_id)
            if u:
                u.balance += total
                u.total_recharged += p.amount
            self.db.commit()
            return True, total
        return False, 0
    
    def create_gift(self, val):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        g = GiftCard(tenant_id=self.tenant_id, code=code, value=float(val))
        self.db.add(g)
        self.db.commit()
        return g
    
    def redeem_gift(self, code, uid):
        g = self.db.query(GiftCard).filter_by(code=code, is_used=False).first()
        if g:
            g.is_used = True
            g.used_by = uid
            g.used_at = datetime.now()
            u = self.get_user(uid)
            if u:
                u.balance += g.value
                u.gifts_redeemed += 1
            self.db.commit()
            return True
        return False
    
    def add_login(self, svc, email, pw, desc='', dur='30 dias', price=0):
        l = Login(
            tenant_id=self.tenant_id, service_name=svc, email=email,
            password=pw, description=desc, duration=dur, price=float(price)
        )
        self.db.add(l)
        self.db.commit()
        return l
    
    def get_available_login(self, svc):
        return self.db.query(Login).filter_by(tenant_id=self.tenant_id, service_name=svc, is_sold=False).first()
    
    def mark_login_sold(self, lid, uid):
        l = self.db.query(Login).filter_by(id=lid).first()
        if l:
            l.is_sold = True
            l.sold_to = uid
            l.sold_at = datetime.now()
            self.db.commit()
    
    def get_stock_count(self):
        return self.db.query(Login).filter_by(tenant_id=self.tenant_id, is_sold=False).count()
    
    def get_stock_list(self):
        logins = self.db.query(Login).filter_by(tenant_id=self.tenant_id, is_sold=False).all()
        stock = {}
        for l in logins:
            if l.service_name not in stock:
                stock[l.service_name] = 0
            stock[l.service_name] += 1
        return stock
    
    def clear_stock(self):
        c = self.db.query(Login).filter_by(tenant_id=self.tenant_id, is_sold=False).delete()
        self.db.commit()
        return c
    
    def remove_by_platform(self, svc):
        c = self.db.query(Login).filter_by(tenant_id=self.tenant_id, service_name=svc, is_sold=False).delete()
        self.db.commit()
        return c
    
    def update_price_by_service(self, svc, price):
        c = self.db.query(Login).filter_by(tenant_id=self.tenant_id, service_name=svc, is_sold=False).update({'price': price})
        self.db.commit()
        return c
    
    def update_all_prices(self, price):
        c = self.db.query(Login).filter_by(tenant_id=self.tenant_id, is_sold=False).update({'price': price})
        self.db.commit()
        return c
    
    def get_stats(self):
        return {
            'users': self.db.query(User).filter_by(tenant_id=self.tenant_id).count(),
            'products': self.db.query(Product).filter_by(tenant_id=self.tenant_id, active=True).count(),
            'sales': self.db.query(Purchase).filter_by(tenant_id=self.tenant_id).count(),
            'today_sales': self.db.query(Purchase).filter_by(tenant_id=self.tenant_id).filter(Purchase.purchase_date >= datetime.now().date()).count(),
            'total_revenue': sum(p.amount for p in self.db.query(Purchase).filter_by(tenant_id=self.tenant_id).all()) if self.db.query(Purchase).filter_by(tenant_id=self.tenant_id).count() > 0 else 0,
            'today_revenue': sum(p.amount for p in self.db.query(Purchase).filter_by(tenant_id=self.tenant_id).filter(Purchase.purchase_date >= datetime.now().date()).all()),
            'month_revenue': sum(p.amount for p in self.db.query(Purchase).filter_by(tenant_id=self.tenant_id).filter(Purchase.purchase_date >= datetime.now().replace(day=1)).all()),
            'total_recharges': self.db.query(PixRecharge).filter_by(tenant_id=self.tenant_id, status='completed').count(),
            'logins_stock': self.db.query(Login).filter_by(tenant_id=self.tenant_id, is_sold=False).count(),
        }
    
    def get_top_products(self, limit=10):
        return self.db.query(Product).filter_by(tenant_id=self.tenant_id, active=True).order_by(Product.total_sold.desc()).limit(limit).all()
    
    def get_top_buyers(self, limit=10):
        return self.db.query(User).filter_by(tenant_id=self.tenant_id).order_by(User.total_purchases.desc()).limit(limit).all()
    
    def get_top_rechargers(self, limit=10):
        return self.db.query(User).filter_by(tenant_id=self.tenant_id).order_by(User.total_recharged.desc()).limit(limit).all()
    
    def get_top_balance(self, limit=20):
        return self.db.query(User).filter_by(tenant_id=self.tenant_id).order_by(User.balance.desc()).limit(limit).all()
    
    def get_recent_rechargers(self, limit=10):
        cutoff = datetime.now() - timedelta(days=30)
        recharges = self.db.query(PixRecharge).filter_by(tenant_id=self.tenant_id, status='completed').filter(PixRecharge.created_at >= cutoff).all()
        totals = {}
        for r in recharges:
            if r.user_id not in totals:
                totals[r.user_id] = 0
            totals[r.user_id] += r.amount
        sorted_u = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [(self.db.query(User).filter_by(id=uid).first(), total) for uid, total in sorted_u]
    
    def check_flood(self, uid):
        u = self.get_user(uid)
        if u and u.flood_until and u.flood_until > datetime.now():
            return True
        seconds = int(self.get_setting('flood_seconds', '6'))
        if u:
            u.flood_count += 1
            u.flood_until = datetime.now() + timedelta(seconds=seconds)
            self.db.commit()
        return False
    
    def add_log(self, ltype, uid, msg):
        self.db.add(Log(tenant_id=self.tenant_id, log_type=ltype, user_id=uid, message=msg))
        self.db.commit()
