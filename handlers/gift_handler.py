from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager
from services.gift_service import GiftService

db = DBManager()
gift_states = {}

async def redeem_gift_start(update, context):
    q = update.callback_query
    await q.answer()
    gift_states[q.from_user.id] = True
    
    txt = db.get_setting('gift_text', '🎁 Digite o código do Gift Card:')
    await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Voltar", callback_data='back')]
    ]))

async def redeem_gift_process(update, context):
    user = update.effective_user
    text = update.message.text.strip().upper()
    
    if user.id not in gift_states:
        return
    
    del gift_states[user.id]
    
    gs = GiftService()
    success = gs.redeem(text, user.id)
    gs.close()
    
    if success:
        bal = db.get_balance(user.id)
        await update.message.reply_text(f"✅ Gift Card resgatado!\n💰 Novo saldo: R$ {bal:.2f}")
    else:
        await update.message.reply_text("❌ Código inválido ou já utilizado!")

async def create_gift_admin(update, context):
    user = update.effective_user
    from config.settings import ADMIN_ID
    if user.id != ADMIN_ID:
        return
    
    try:
        amount = float(update.message.text)
        gs = GiftService()
        gift = gs.create(amount)
        gs.close()
        
        await update.message.reply_text(f"✅ Gift Card criado!\n🎁 Código: `{gift.code}`\n💰 Valor: R$ {amount:.2f}")
    except:
        await update.message.reply_text("❌ Valor inválido!")

async def list_gifts(update, context):
    from database.models import SessionLocal, GiftCard
    session = SessionLocal()
    gifts = session.query(GiftCard).filter_by(is_used=False).all()
    
    if not gifts:
        await update.message.reply_text("Nenhum Gift Card disponível!")
    else:
        txt = "🎁 *Gift Cards Disponíveis*\n\n"
        for g in gifts[:20]:
            txt += f"🎁 {g.code} - R$ {g.value:.2f}\n"
        await update.message.reply_text(txt, parse_mode='Markdown')
    
    session.close()
