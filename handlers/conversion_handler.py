from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager

db = DBManager()
conversion_states = {}

async def start_conversion(update, context):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    db_user = db.get_user(user.id)
    
    if not db_user:
        return
    
    pts = db_user.affiliate_points
    mult = float(db.get_setting('affiliate_multiplier', '0.01'))
    min_pts = int(db.get_setting('affiliate_min_points', '500'))
    val = pts * mult
    
    txt = db.get_setting('convert_text', '')
    txt = txt.replace('{pontos}', str(pts))
    txt = txt.replace('{valor}', f'R$ {val:.2f}')
    txt = txt.replace('{min_pontos}', str(min_pts))
    
    if pts < min_pts:
        await q.edit_message_text(
            f"❌ Você precisa de no mínimo {min_pts} pontos para converter!\n"
            f"Seus pontos: {pts}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Voltar", callback_data='m2')]
            ])
        )
        return
    
    conversion_states[user.id] = True
    sec = db.get_setting('convert_seconds', '80')
    
    await q.edit_message_text(
        txt + f"\n\n⏳ Você tem {sec} segundos para responder.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Cancelar", callback_data='m2')]
        ])
    )

async def process_conversion(update, context):
    user = update.effective_user
    text = update.message.text
    
    if user.id not in conversion_states:
        return
    
    try:
        qty = int(text)
        db_user = db.get_user(user.id)
        
        if not db_user:
            del conversion_states[user.id]
            return
        
        if qty > db_user.affiliate_points:
            await update.message.reply_text("❌ Pontos insuficientes!")
            del conversion_states[user.id]
            return
        
        mult = float(db.get_setting('affiliate_multiplier', '0.01'))
        val = qty * mult
        
        db_user.affiliate_points -= qty
        db_user.balance += val
        db.db.commit()
        
        await update.message.reply_text(
            f"✅ Conversão realizada!\n"
            f"📥 Pontos convertidos: {qty}\n"
            f"💰 Valor creditado: R$ {val:.2f}\n"
            f"💵 Novo saldo: R$ {db_user.balance:.2f}"
        )
        
        del conversion_states[user.id]
        
    except ValueError:
        await update.message.reply_text("❌ Digite apenas números!")

async def check_conversion_timeout(context):
    to_remove = []
    for uid in list(conversion_states.keys()):
        if uid in conversion_states:
            del conversion_states[uid]
            try:
                await context.bot.send_message(uid, "⏰ Tempo esgotado para conversão!")
            except:
                pass
