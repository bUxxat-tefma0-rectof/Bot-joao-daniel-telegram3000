from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class MessageUtils:
    @staticmethod
    def create_button(text, callback_data):
        return InlineKeyboardButton(text, callback_data=callback_data)
    
    @staticmethod
    def create_url_button(text, url):
        return InlineKeyboardButton(text, url=url)
    
    @staticmethod
    def create_keyboard(buttons, columns=1):
        kb = []
        row = []
        for btn in buttons:
            row.append(btn)
            if len(row) >= columns:
                kb.append(row)
                row = []
        if row:
            kb.append(row)
        return InlineKeyboardMarkup(kb)
    
    @staticmethod
    def create_back_button(callback_data='back'):
        return InlineKeyboardButton("🔙 Voltar", callback_data=callback_data)
    
    @staticmethod
    def create_pagination_keyboard(current_page, total_pages, prefix='page'):
        kb = []
        row = []
        if current_page > 0:
            row.append(InlineKeyboardButton("⬅️ Anterior", callback_data=f'{prefix}_{current_page-1}'))
        if current_page < total_pages - 1:
            row.append(InlineKeyboardButton("➡️ Próximo", callback_data=f'{prefix}_{current_page+1}'))
        if row:
            kb.append(row)
        kb.append([InlineKeyboardButton(f"📄 {current_page+1}/{total_pages}", callback_data='none')])
        return InlineKeyboardMarkup(kb)
    
    @staticmethod
    def create_confirm_keyboard(yes_data, no_data):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Sim", callback_data=yes_data),
             InlineKeyboardButton("❌ Não", callback_data=no_data)]
        ])
    
    @staticmethod
    def format_product_list(products, show_price=True, show_stock=True):
        text = ""
        for p in products:
            text += f"📦 {p.name}"
            if show_price: text += f" - R$ {p.price:.2f}"
            if show_stock: text += f" ({p.stock} unid.)"
            text += "\n"
        return text
    
    @staticmethod
    def format_purchase_list(purchases):
        text = ""
        for p in purchases:
            text += f"🛍 {p.product_name}\n"
            text += f"⏰ {p.purchase_date.strftime('%d/%m/%Y')}\n"
            text += f"💰 R$ {p.amount:.2f}\n"
            if p.email: text += f"📧 {p.email}\n"
            text += "\n"
        return text
