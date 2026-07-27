from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager
from database.models import SessionLocal, Cart, Product

db = DBManager()
user_carts = {}

async def add_to_cart(update, context, user_id, product_id, quantity=1):
    session = SessionLocal()
    existing = session.query(Cart).filter_by(user_id=user_id, product_id=product_id).first()
    
    if existing:
        existing.quantity += quantity
    else:
        cart = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        session.add(cart)
    
    session.commit()
    session.close()
    
    product = db.get_product(product_id)
    await update.message.reply_text(f"✅ {product.name} adicionado ao carrinho!")

async def view_cart(update, context, user_id):
    session = SessionLocal()
    items = session.query(Cart).filter_by(user_id=user_id).all()
    
    if not items:
        await update.message.reply_text("🛒 Carrinho vazio!")
        session.close()
        return
    
    total = 0
    txt = "🛒 *Seu Carrinho*\n\n"
    kb = []
    
    for item in items:
        product = db.get_product(item.product_id)
        if product:
            subtotal = product.price * item.quantity
            total += subtotal
            txt += f"📦 {product.name}\n"
            txt += f"   Qtd: {item.quantity} | R$ {subtotal:.2f}\n\n"
            kb.append([InlineKeyboardButton(f"❌ Remover {product.name}", 
                                            callback_data=f'cart_remove_{item.id}')])
    
    txt += f"💰 *Total: R$ {total:.2f}*"
    kb.append([InlineKeyboardButton("💳 Finalizar Compra", callback_data=f'cart_checkout')])
    kb.append([InlineKeyboardButton("🗑️ Esvaziar Carrinho", callback_data='cart_clear')])
    kb.append([InlineKeyboardButton("🔙 Voltar", callback_data='back')])
    
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    session.close()

async def remove_from_cart(update, context, cart_id):
    session = SessionLocal()
    item = session.query(Cart).filter_by(id=cart_id).first()
    if item:
        session.delete(item)
        session.commit()
    session.close()
    await update.callback_query.answer("✅ Removido!")

async def clear_cart(update, context, user_id):
    session = SessionLocal()
    session.query(Cart).filter_by(user_id=user_id).delete()
    session.commit()
    session.close()
    await update.callback_query.edit_message_text("🛒 Carrinho esvaziado!")

async def checkout(update, context, user_id):
    session = SessionLocal()
    items = session.query(Cart).filter_by(user_id=user_id).all()
    
    if not items:
        await update.callback_query.edit_message_text("🛒 Carrinho vazio!")
        session.close()
        return
    
    total = 0
    for item in items:
        product = db.get_product(item.product_id)
        if product:
            total += product.price * item.quantity
    
    bal = db.get_balance(user_id)
    
    if bal >= total:
        for item in items:
            product = db.get_product(item.product_id)
            if product and product.stock >= item.quantity:
                for _ in range(item.quantity):
                    db.subtract_balance(user_id, product.price)
                    db.decrease_stock(product.id)
                    from services.login_service import LoginService
                    ls = LoginService()
                    login = ls.get(product.name)
                    email = login.email if login else ''
                    pw = login.password if login else ''
                    if login: ls.sold(login.id, user_id)
                    db.create_purchase(user_id, product.name, product.price, email, pw, '')
                    ls.close()
        
        session.query(Cart).filter_by(user_id=user_id).delete()
        session.commit()
        await update.callback_query.edit_message_text(f"✅ Compra finalizada! Total: R$ {total:.2f}")
    else:
        falta = total - bal
        txt = db.get_setting('insufficient_text', '')
        txt = txt.replace('{saldo}', f'R$ {bal:.2f}').replace('{preco}', f'R$ {total:.2f}').replace('{falta}', f'R$ {falta:.2f}')
        kb = [[InlineKeyboardButton(f"Gerar PIX R$ {total:.2f}", callback_data=f'pixbuy_{total}')]]
        await update.callback_query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    
    session.close()
