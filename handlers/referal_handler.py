from database.db_manager import DBManager
from database.models import SessionLocal, User

db = DBManager()

async def process_referral(user_id, referral_code):
    session = SessionLocal()
    referrer = session.query(User).filter_by(referral_code=referral_code).first()
    referred = session.query(User).filter_by(telegram_id=user_id).first()
    if referrer and referred and referrer.id != referred.id and not referred.referred_by:
        referred.referred_by = referrer.telegram_id
        session.commit()
        session.close()
        return True
    session.close()
    return False

async def get_referral_stats(user_id):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=user_id).first()
    if not user:
        session.close()
        return None
    referred_users = session.query(User).filter_by(referred_by=user_id).all()
    stats = {
        'total_referrals': len(referred_users),
        'commission_balance': user.commission_balance,
        'affiliate_points': user.affiliate_points,
        'referral_code': user.referral_code,
        'referral_link': f"https://t.me/bot?start={user.telegram_id}"
    }
    session.close()
    return stats

async def claim_commission(user_id):
    user = db.get_user(user_id)
    if user and user.commission_balance > 0:
        amount = user.commission_balance
        user.balance += amount
        user.commission_balance = 0
        db.db.commit()
        return amount
    return 0
