from database.db_manager import DBManager
from database.models import SessionLocal, Alert, Product

db = DBManager()

async def toggle_alert(update, context):
    q = update.callback_query
    user_id = q.from_user.id
    data = q.data
    if data.startswith('alert_'):
        product_id = int(data.replace('alert_', ''))
        session = SessionLocal()
        existing = session.query(Alert).filter_by(user_id=user_id, product_id=product_id).first()
        if existing:
            existing.active = not existing.active
            status = "ATIVADO" if existing.active else "DESATIVADO"
        else:
            session.add(Alert(user_id=user_id, product_id=product_id, active=True))
            status = "ATIVADO"
        session.commit()
        session.close()
        await q.answer(f"✅ {status}!")

async def check_alerts(bot):
    session = SessionLocal()
    active_alerts = session.query(Alert).filter_by(active=True).all()
    for alert in active_alerts:
        product = session.query(Product).filter_by(id=alert.product_id, active=True).first()
        if product and product.stock > 0:
            try:
                await bot.send_message(alert.user_id, f"🔔 {product.name} abastecido!\nEstoque: {product.stock}\nPreço: R$ {product.price:.2f}")
                alert.active = False
            except: pass
    session.commit()
    session.close()
