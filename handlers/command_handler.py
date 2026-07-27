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
    txt = db.get_setting('support_text', '')
    if link:
        await update.message.reply_text(f"{txt}\n{link}")
    else:
        await update.message.reply_text(txt)

async def cmd_alertas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from database.models import SessionLocal, Alert, Product
    session = SessionLocal()
    alerts = session.query(Alert).filter_by(user_id=update.effective_user.id, active=True).all()
    
    if not alerts:
        await update.message.reply_text("Nenhum alerta ativo.")
    else:
        txt = "🔔 Seus alertas ativos:\n\n"
        for a in alerts:
            p = session.query(Product).filter_by(id=a.product_id).first()
            if p:
                txt += f"📦 {p.name}\n"
        await update.message.reply_text(txt)
    
    session.close()

async def cmd_afiliados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    from handlers.referral_handler import get_referral_stats
    stats = await get_referral_stats(user.id)
    
    if stats:
        txt = "💼 *Afiliados*\n\n"
        txt += f"👥 Indicados: {stats['total_referrals']}\n"
        txt += f"💰 Comissão: R$ {stats['commission_balance']:.2f}\n"
        txt += f"🔗 Link: {stats['referral_link']}"
        await update.message.reply_text(txt, parse_mode='Markdown')

async def cmd_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❌ Use: /gift CODIGO")
        return
    
    from services.gift_service import GiftService
    gs = GiftService()
    success = gs.redeem(args[0].upper(), update.effective_user.id)
    gs.close()
    
    if success:
        await update.message.reply_text(f"✅ Gift Card resgatado!\n💰 Saldo: R$ {db.get_balance(update.effective_user.id):.2f}")
    else:
        await update.message.reply_text("❌ Código inválido!")

async def cmd_pesquisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("❌ Use: /pesquisar NOME")
        return
    
    search = ' '.join(args).lower()
    products = db.get_products()
    results = [p for p in products if search in p.name.lower()]
    
    if not results:
        await update.message.reply_text("❌ Nenhum produto encontrado!")
        return
    
    txt = f"🔍 Resultados para '{search}':\n\n"
    for p in results[:10]:
        txt += f"📦 {p.name} - R$ {p.price:.2f} ({p.stock} unid.)\n"
    
    await update.message.reply_text(txt)
