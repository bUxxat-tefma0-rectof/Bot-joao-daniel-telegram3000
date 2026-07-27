import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config.settings import BOT_TOKEN, ADMIN_ID
from database.models import init_db
from database.db_manager import DBManager

from handlers.client_handler import start, callback, handle_msg, waiting, db as cdb
from handlers.admin_handler import admin, adm_callback, admin_states, handle_admin_message
from handlers.payment_handler import check_pix_callback

from services.gift_service import GiftService

from utils.logger import logger

import threading

db = DBManager()

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    
    if user.id == ADMIN_ID and user.id in admin_states:
        await handle_admin_message(update, context)
        return
    
    if user.id in waiting:
        state = waiting[user.id]
        
        if state == 'recharge_value':
            try:
                amount = float(text)
                mn = float(db.get_setting('deposit_min', '2'))
                mx = float(db.get_setting('deposit_max', '150'))
                if amount < mn:
                    await update.message.reply_text(f"❌ Mín R$ {mn:.2f}")
                elif amount > mx:
                    await update.message.reply_text(f"❌ Máx R$ {mx:.2f}")
                else:
                    await update.message.reply_text("⏳ Gerando...")
                    from handlers.client_handler import gen_pix
                    await gen_pix(update.message, user, amount, db.get_balance(user.id))
            except:
                await update.message.reply_text("❌ Inválido!")
            del waiting[user.id]
        
        elif state.startswith('multi_'):
            try:
                qty = int(text)
                pid = int(state.replace('multi_', ''))
                p = db.get_product(pid)
                bal = db.get_balance(user.id)
                total = p.price * qty
                if qty > p.stock:
                    await update.message.reply_text(f"❌ Estoque: {p.stock}")
                elif bal < total:
                    falta = total - bal
                    kb = [[InlineKeyboardButton(f"Gerar PIX R$ {total:.2f}", callback_data=f'pixbuy_{total}')]]
                    await update.message.reply_text(f"❌ Falta R$ {falta:.2f}", reply_markup=InlineKeyboardMarkup(kb))
                else:
                    for _ in range(qty):
                        db.subtract_balance(user.id, p.price)
                        db.decrease_stock(pid)
                    await update.message.reply_text(f"✅ {qty}x {p.name}")
            except:
                await update.message.reply_text("❌ Inválido!")
            del waiting[user.id]
        
        elif state == 'convert_points':
            try:
                pts = int(text)
                db_user = db.get_user(user.id)
                mult = float(db.get_setting('affiliate_multiplier', '0.01'))
                if pts <= db_user.affiliate_points:
                    val = pts * mult
                    db_user.affiliate_points -= pts
                    db_user.balance += val
                    db.db.commit()
                    await update.message.reply_text(f"✅ R$ {val:.2f}")
                else:
                    await update.message.reply_text("❌ Pontos insuficientes!")
            except:
                await update.message.reply_text("❌ Inválido!")
            del waiting[user.id]
        
        elif state == 'gift_code':
            gs = GiftService()
            if gs.redeem(text.strip().upper(), user.id):
                await update.message.reply_text(f"✅ Resgatado! Saldo: R$ {db.get_balance(user.id):.2f}")
            else:
                await update.message.reply_text("❌ Inválido!")
            gs.close()
            del waiting[user.id]
        
        elif state == 'edit_whatsapp':
            db_user = db.get_user(user.id)
            if text.lower() == 'remover':
                db_user.whatsapp = None
            else:
                db_user.whatsapp = text
            db.db.commit()
            await update.message.reply_text("✅ Salvo!")
            del waiting[user.id]
        
        return
    
    await handle_msg(update, context)

async def handle_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id == ADMIN_ID and user.id in admin_states:
        field = admin_states[user.id]
        if field in ['welcome_image', 'image']:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            import os
            os.makedirs('images', exist_ok=True)
            file_path = f"images/welcome_{user.id}.jpg"
            await file.download_to_drive(file_path)
            db.set_setting('welcome_image', file_path)
            await update.message.reply_text("✅ Imagem salva com sucesso!")
            del admin_states[user.id]

def main():
    print("🐕 INICIANDO BOT...")
    print("📦 Inicializando banco de dados...")
    init_db()
    print("✅ Banco de dados pronto!")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('admin', admin))
    
    # Callbacks do admin
    app.add_handler(CallbackQueryHandler(adm_callback, pattern='^adm_'))
    
    # Callbacks de pagamento
    app.add_handler(CallbackQueryHandler(check_pix_callback, pattern='^(check_pix_|copy_pix_)'))
    
    # Callbacks do cliente (menu principal)
    app.add_handler(CallbackQueryHandler(callback, pattern='^(m[1-8]|cat_|prod_|buy_|multi_|pixbuy_|back|recarga_pix|history|convert|none|rank_)$'))
    
    # Mensagens
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
    
    # Fotos
    app.add_handler(MessageHandler(filters.PHOTO, handle_photos))
    
    print("✅ Handlers configurados!")
    print("🚀 Bot online!")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False)

if __name__ == '__main__':
    main()
