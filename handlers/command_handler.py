from telegram import Update
from telegram.ext import ContextTypes
from database.db_manager import DBManager
from services.pix_service import PixService
from services.pdf_service import PDFService

db = DBManager()

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.client_handler import start
    await start(update, context)

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.admin_handler import admin
    await admin(update, context)

async def cmd_pix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    
    if not args:
        await update.message.reply_text("❌ Use: /pix VALOR\nExemplo: /pix 10")
        return
    
    try:
        amount = float(args[0])
        mn = float(db.get_setting('deposit_min', '2'))
        mx = float(db.get_setting('deposit_max', '150'))
        
        if amount < mn:
            await update.message.reply_text(f"❌ Valor mínimo: R$ {mn:.2f}")
            return
        if amount > mx:
            await update.message.reply_text(f"❌ Valor máximo: R$ {mx:.2f}")
            return
        
        await update.message.reply_text("⏳ Gerando PIX...")
        from handlers.client_handler import gen_pix
        bal = db.get_balance(user.id)
        await gen_pix(update.message, user, amount, bal)
        
    except ValueError:
        await update.message.reply_text("❌ Valor inválido!")

async def cmd_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bal = db.get_balance(user.id)
    await update.message.reply_text(f"💰 Seu saldo: R$ {bal:.2f}")

async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"🆔 Seu ID: {user.id}")

async def cmd_historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    purchases = db.get_user_purchases(user.id)
    
    if not purchases:
        await update.message.reply_text("Nenhuma compra encontrada.")
        return
    
    pdf = PDFService.generate_history(
        {'id': str(user.id), 'nome': user.first_name or '', 'saldo': db.get_balance(user.id)},
        purchases
    )
    
    await update.message.reply_document(document=pdf, filename='historico.pdf')

async def cmd_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.ranking_handler import show_ranking_detail
    await show_ranking_detail(update, context)

async def cmd_termos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = db.get_setting('terms_text', 'Termos não configurados.')
    await update.message.reply_text(txt, parse_mode='Markdown')

async def cmd_suporte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = db.get_setting('support_link', '')
