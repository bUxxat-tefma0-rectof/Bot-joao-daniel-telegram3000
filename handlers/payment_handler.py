from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager
from services.pix_service import PixService
from services.affiliate_service import AffiliateService
from services.login_service import LoginService
from datetime import datetime

db = DBManager()

async def process_payment(update, context, user, amount, bal, product_id=None, quantity=1):
    ps = PixService()
    result = ps.gerar_pix(user.id, amount, "Pagamento")
    
    if result['sucesso']:
        bonus_pct = float(db.get_setting('bonus_percentage', '0'))
        bonus_min = float(db.get_setting('bonus_min_value', '10'))
        bonus = amount * (bonus_pct/100) if amount >= bonus_min and bonus_pct > 0 else 0
        
        db.create_pix(user.id, amount, result['pix_id'], '', result['copia_cola'], 
                      datetime.now() + __import__('datetime').timedelta(minutes=int(db.get_setting('pix_expiration', '15'))))
        
        txt = db.get_setting('pix_result_text', '')
        txt = txt.replace('{valor}', f'R$ {amount:.2f}').replace('{id}', result['pix_id'])
        txt = txt.replace('{copia_cola}', result['copia_cola']).replace('{saldo}', f'R$ {bal:.2f}')
        txt = txt.replace('{bonus}', f'R$ {bonus:.2f}').replace('{total}', f'R$ {bal + amount + bonus:.2f}')
        txt = txt.replace('{expiracao}', str(result['expiracao_minutos']))
        
        kb = [
            [InlineKeyboardButton(db.get_setting('wait_btn', 'Aguardando'), 
                                  callback_data=f'check_pix_{result["pix_id"]}_{product_id or 0}_{quantity}')],
            [InlineKeyboardButton(db.get_setting('copy_btn', 'Copiar PIX'), 
                                  callback_data=f'copy_pix_{result["pix_id"]}')]
        ]
        
        if result.get('qr_code_imagem'):
            msg = await update.message.reply_photo(photo=result['qr_code_imagem'], 
                                                    caption=txt, 
                                                    reply_markup=InlineKeyboardMarkup(kb))
        else:
            msg = await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))
        
        return msg
    ps.close()
    return None

async def check_pix_callback(update, context):
    q = update.callback_query
    await q.answer()
    d = q.data
    u = q.from_user
    
    if d.startswith('check_pix_'):
        parts = d.replace('check_pix_', '').split('_')
        pix_id = parts[0]
        product_id = int(parts[1]) if len(parts) > 1 else 0
        quantity = int(parts[2]) if len(parts) > 2 else 1
        
        ps = PixService()
        result = ps.verificar(pix_id)
        
        if result.get('aprovado'):
            success, total = db.confirm_pix(pix_id)
            if success:
                af = AffiliateService()
                af.add_commission(u.id, total)
                af.close()
                
                if product_id > 0:
                    p = db.get_product(product_id)
                    if p:
                        total_price = p.price * quantity
                        if db.get_balance(u.id) >= total_price:
                            for _ in range(quantity):
                                db.subtract_balance(u.id, p.price)
                                db.decrease_stock(product_id)
                                ls = LoginService()
                                login = ls.get(p.name)
                                email = login.email if login else ''
                                pw = login.password if login else ''
                                if login: ls.sold(login.id, u.id)
                                db.create_purchase(u.id, p.name, p.price, email, pw, '')
                                ls.close()
                            
                            txt = db.get_setting('success_text', 'Compra realizada!')
                            txt = txt.replace('{nome}', p.name).replace('{quantidade}', str(quantity))
                            await q.edit_message_text(txt)
                        else:
                            await q.edit_message_text("❌ Erro ao processar compra!")
                else:
                    txt = f"✅ Pagamento aprovado!\n💰 Saldo: R$ {db.get_balance(u.id):.2f}"
                    await q.edit_message_text(txt)
            else:
                await q.edit_message_text("✅ Pagamento aprovado!")
        elif result.get('status') == 'pending':
            await q.answer("⏳ Ainda aguardando pagamento...", show_alert=True)
        else:
            await q.edit_message_text(db.get_setting('expired_pix_text', 'PIX Expirado').replace('{id}', pix_id))
        ps.close()
    
    elif d.startswith('copy_pix_'):
        pix_id = d.replace('copy_pix_', '')
        from database.models import SessionLocal, PixRecharge
        session = SessionLocal()
        pix = session.query(PixRecharge).filter_by(pix_id=pix_id).first()
        if pix:
            await q.answer(f"📋 PIX copiado!", show_alert=True)
        session.close()

async def check_expired_payments():
    from database.models import SessionLocal, PixRecharge
    session = SessionLocal()
    expired = session.query(PixRecharge).filter(
        PixRecharge.status == 'pending',
        PixRecharge.expires_at < datetime.now()
    ).all()
    
    for p in expired:
        p.status = 'expired'
    
    session.commit()
    session.close()
