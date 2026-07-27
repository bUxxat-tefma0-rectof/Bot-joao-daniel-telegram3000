from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager
from services.login_service import LoginService

db = DBManager()

async def view_stock(update, context):
    stock = db.get_stock_list()
    
    if not stock:
        await update.message.reply_text("📦 Estoque vazio!")
        return
    
    txt = db.get_setting('stock_text', '📦 *Estoque de Logins*\n\n')
    for name, qty in stock.items():
        txt += f"📦 {name}: {qty} unid.\n"
    
    kb = [[InlineKeyboardButton("🔙 Voltar", callback_data='back')]]
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def add_stock(update, context):
    user = update.effective_user
    from config.settings import ADMIN_ID
    if user.id != ADMIN_ID:
        return
    
    q = update.callback_query
    await q.answer()
    
    txt = "📦 *Adicionar Login*\n\nFormato:\n`SERVICO|EMAIL|SENHA|DESCRICAO|DURACAO|PRECO`\n\nUse | como separador"
    await q.edit_message_text(txt, parse_mode='Markdown')

async def remove_stock(update, context):
    user = update.effective_user
    from config.settings import ADMIN_ID
    if user.id != ADMIN_ID:
        return
    
    try:
        service = update.message.text.strip()
        ls = LoginService()
        count = ls.remove(service)
        ls.close()
        await update.message.reply_text(f"✅ {count} logins removidos de {service}!")
    except:
        await update.message.reply_text("❌ Erro ao remover!")

async def stock_detail(update, context):
    from database.models import SessionLocal, Login
    session = SessionLocal()
    logins = session.query(Login).filter_by(is_sold=False).all()
    
    txt = "📊 *Estoque Detalhado*\n\n"
    for l in logins[:50]:
        txt += f"📦 {l.service_name}\n📧 {l.email}\n🔐 {l.password}\n💰 R$ {l.price:.2f}\n\n"
    
    await update.message.reply_text(txt, parse_mode='Markdown')
    session.close()
