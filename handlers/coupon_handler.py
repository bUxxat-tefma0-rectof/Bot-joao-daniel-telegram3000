from database.db_manager import DBManager
from database.models import SessionLocal, Coupon

db = DBManager()

async def create_coupon(update, context):
    import random, string
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    session = SessionLocal()
    coupon = Coupon(
        tenant_id=1,
        code=code,
        discount_percent=float(context.args[0]) if context.args else 10,
        max_uses=int(context.args[1]) if len(context.args) > 1 else 100,
        active=True
    )
    session.add(coupon)
    session.commit()
    session.close()
    
    await update.message.reply_text(f"✅ Cupom criado!\nCódigo: `{code}`\nDesconto: {coupon.discount_percent}%")

async def apply_coupon(update, context):
    text = update.message.text.strip().upper()
    session = SessionLocal()
    coupon = session.query(Coupon).filter_by(code=text, active=True).first()
    
    if coupon:
        if coupon.max_uses > coupon.used_count:
            await update.message.reply_text(f"✅ Cupom aplicado! {coupon.discount_percent}% de desconto!")
            coupon.used_count += 1
        else:
            await update.message.reply_text("❌ Cupom esgotado!")
    else:
        await update.message.reply_text("❌ Cupom inválido!")
    
    session.commit()
    session.close()
