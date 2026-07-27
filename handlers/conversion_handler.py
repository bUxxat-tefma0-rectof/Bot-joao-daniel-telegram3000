from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager

db = DBManager()
conversion_states = {}

async def start_conversion(update, context):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    db_user = db.get_user(user.id)
    if not db_user: return
    
    pts = db_user.affiliate_points
    mult = float(db.get_setting('affiliate_multiplier', '0.01'))
    min_pts = int(db.get_setting('affiliate_min_points', '500'))
    val = pts * mult
    
    txt = db.get_setting('convert_text', '')
    txt = txt.replace('{pontos}', str(pts)).replace('{valor}', f'R$ {val:.2f}').replace('{min_pontos}', str(min_pts))
    
    if pts < min_pts:
        await q.edit_message_text(f"❌ Mínimo {min_pts} pontos! Você tem {pts}.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Voltar", callback_data='m2')]]))
        return
    
    conversion_states[user.id] = True
    sec = db.get_setting('convert_seconds', '80')
    await q.edit_message_text(txt + f"\n\n⏳ {sec} segundos para responder.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancelar", callback_data='m2')]]))

async def process_conversion(update, context):
    user = update.effective_user
    text = update.message.text
    if user.id not in conversion_states: return
    try:
        qty = int(text)
        db_user = db.get_user(user.id)
        if not db_user: return
        if qty > db_user.affiliate_points:
            await update.message.reply_text("❌ Pontos insuficientes!"); del conversion_states[user.id]; return
        mult = float(db.get_setting('affiliate_multiplier', '0.01'))
        val = qty * mult
        db_user.affiliate_points -= qty
        db_user.balance += val
        db.db.commit()
        await update.message.reply_text(f"✅ Convertido!\n💰 R$ {val:.2f} adicionado!")
        del conversion_states[user.id]
    except ValueError:
        await update.message.reply_text("❌ Digite apenas números!")
