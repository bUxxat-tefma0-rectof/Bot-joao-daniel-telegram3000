from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager

db = DBManager()
support_tickets = {}

async def open_ticket(update, context):
    user = update.effective_user
    support_tickets[user.id] = {'status': 'open', 'messages': []}
    
    txt = db.get_setting('support_text', '')
    link = db.get_setting('support_link', '')
    
    if link:
        await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Falar com Suporte", url=link)],
            [InlineKeyboardButton("🔙 Voltar", callback_data='back')]
        ]))
    else:
        await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Voltar", callback_data='back')]
        ]))

async def close_ticket(update, context):
    user = update.effective_user
    if user.id in support_tickets:
        support_tickets[user.id]['status'] = 'closed'
        await update.message.reply_text("✅ Atendimento encerrado!")

async def ticket_status(update, context):
    user = update.effective_user
    if user.id in support_tickets:
        status = support_tickets[user.id]['status']
        msg_count = len(support_tickets[user.id]['messages'])
        await update.message.reply_text(f"📊 Status: {status}\n📝 Mensagens: {msg_count}")
    else:
        await update.message.reply_text("Nenhum atendimento em aberto.")
