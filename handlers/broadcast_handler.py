from database.models import SessionLocal, User
from telegram import Update

broadcast_states = {}

async def start_broadcast(update, context):
    user = update.effective_user
    from config.settings import ADMIN_ID
    if user.id != ADMIN_ID:
        return
    
    q = update.callback_query
    await q.answer()
    broadcast_states[user.id] = {'type': 'text'}
    
    await q.edit_message_text("📤 Envie a mensagem que deseja transmitir para todos os usuários:")

async def start_broadcast_photo(update, context):
    user = update.effective_user
    from config.settings import ADMIN_ID
    if user.id != ADMIN_ID:
        return
    
    q = update.callback_query
    await q.answer()
    broadcast_states[user.id] = {'type': 'photo'}
    
    await q.edit_message_text("📤 Envie a foto com legenda para transmitir:")

async def execute_broadcast_text(update, context):
    user = update.effective_user
    if user.id not in broadcast_states:
        return
    
    del broadcast_states[user.id]
    text = update.message.text
    
    session = SessionLocal()
    users = session.query(User).all()
    count = 0
    
    for u in users:
        try:
            await context.bot.send_message(u.telegram_id, text)
            count += 1
        except:
            pass
    
    session.close()
    await update.message.reply_text(f"✅ Transmissão concluída!\n📤 Enviado para {count} usuários.")

async def execute_broadcast_photo(update, context):
    user = update.effective_user
    if user.id not in broadcast_states:
        return
    
    del broadcast_states[user.id]
    photo = update.message.photo[-1]
    caption = update.message.caption or ''
    
    session = SessionLocal()
    users = session.query(User).all()
    count = 0
    
    for u in users:
        try:
            await context.bot.send_photo(u.telegram_id, photo.file_id, caption=caption)
            count += 1
        except:
            pass
    
    session.close()
    await update.message.reply_text(f"✅ Transmissão concluída!\n📤 Enviado para {count} usuários.")
