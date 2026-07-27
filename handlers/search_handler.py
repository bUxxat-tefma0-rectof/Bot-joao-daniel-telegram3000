from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager

db = DBManager()
search_states = {}

async def start_search(update, context):
    q = update.callback_query
    await q.answer()
    search_states[q.from_user.id] = True
    await q.edit_message_text("🔍 Digite o nome do produto que deseja pesquisar:",
                              reply_markup=InlineKeyboardMarkup([
                                  [InlineKeyboardButton("🔙 Voltar", callback_data='back')]
                              ]))

async def do_search(update, context):
    user = update.effective_user
    text = update.message.text
    
    if user.id not in search_states:
        return
    
    del search_states[user.id]
    
    products = db.get_products()
    results = [p for p in products if text.lower() in p.name.lower()]
    
    if not results:
        await update.message.reply_text("❌ Nenhum produto encontrado!",
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Voltar", callback_data='back')]
                                        ]))
        return
    
    bal = db.get_balance(user.id)
    txt = f"🔍 Resultados para '*{text}*':\n\n"
    kb = []
    
    for p in results[:10]:
        txt += f"📦 {p.name} - R$ {p.price:.2f} ({p.stock} unid.)\n"
        kb.append([InlineKeyboardButton(f"{p.name} - R$ {p.price:.2f}", callback_data=f'prod_{p.id}')])
    
    kb.append([InlineKeyboardButton("🔙 Voltar", callback_data='back')])
    
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
