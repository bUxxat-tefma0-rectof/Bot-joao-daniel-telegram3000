from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager

db = DBManager()

async def show_rankings(update, context):
    q = update.callback_query
    await q.answer()
    
    txt = db.get_setting('ranking_text', '📊 Selecione o ranking:')
    kb = [
        [InlineKeyboardButton(db.get_setting('rank_balance_btn', 'Top Saldo'), callback_data='rank_balance')],
        [InlineKeyboardButton(db.get_setting('rank_recharge_btn', 'Top Depósitos'), callback_data='rank_recharge')],
        [InlineKeyboardButton(db.get_setting('rank_products_btn', 'Top Produtos'), callback_data='rank_products')],
        [InlineKeyboardButton(db.get_setting('rank_recent_btn', 'Top Recentes'), callback_data='rank_recent')],
        [InlineKeyboardButton("📊 Top Compradores", callback_data='rank_buyers')],
        [InlineKeyboardButton("🔙 Voltar", callback_data='back')]
    ]
    await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def show_ranking_detail(update, context):
    q = update.callback_query
    await q.answer()
    tp = q.data.replace('rank_', '')
    
    if tp == 'balance':
        users = db.get_top_balance(20)
        txt = "🏆 *Top 20 Saldo*\n\n"
        medals = ['🥇', '🥈', '🥉']
        for i, u in enumerate(users, 1):
            name = u.first_name or f"ID:{u.telegram_id}"
            medal = medals[i-1] if i <= 3 else f'{i}º'
            txt += f"{medal} {name}\n   💰 R$ {u.balance:.2f}\n\n"
    
    elif tp == 'recharge':
        users = db.get_top_rechargers(10)
        txt = "💠 *Top 10 Depósitos*\n\n"
        for i, u in enumerate(users, 1):
            name = u.first_name or f"ID:{u.telegram_id}"
            medal = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else f'{i}º'
            txt += f"{medal} {name}\n   💰 R$ {u.total_recharged:.2f}\n\n"
    
    elif tp == 'products':
        products = db.get_top_products(10)
        txt = "📦 *Top 10 Produtos*\n\n"
        for i, p in enumerate(products, 1):
            medal = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else f'{i}º'
            txt += f"{medal} {p.name}\n   🛒 {p.total_sold} vendas\n\n"
    
    elif tp == 'recent':
        users = db.get_recent_rechargers(10)
        txt = "📈 *Top 10 Recentes*\n\n"
        for i, (u, total) in enumerate(users, 1):
            name = u.first_name or f"ID:{u.telegram_id}"
            medal = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else f'{i}º'
            txt += f"{medal} {name}\n   💰 R$ {total:.2f}\n\n"
    
    elif tp == 'buyers':
        users = db.get_top_buyers(10)
        txt = "🛒 *Top 10 Compradores*\n\n"
        for i, u in enumerate(users, 1):
            name = u.first_name or f"ID:{u.telegram_id}"
            medal = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else f'{i}º'
            txt += f"{medal} {name}\n   🛒 {u.total_purchases} compras\n\n"
    
    await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Voltar", callback_data='m5')]
    ]), parse_mode='Markdown')
