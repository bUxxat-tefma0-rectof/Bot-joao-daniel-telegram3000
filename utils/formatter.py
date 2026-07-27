class TextFormatter:
    @staticmethod
    def menu_header(title):
        return f"╭{'─'*30}╮\n│  {title.center(26)}  │\n╰{'─'*30}╯"
    
    @staticmethod
    def user_info(user_id, balance, extra=''):
        text = f"💠 Seus Dados:\n"
        text += f"├👤 ID: {user_id}\n"
        text += f"└💰 Saldo: R$ {balance:.2f}\n"
        if extra: text += f"{extra}\n"
        return text
    
    @staticmethod
    def product_card(product, user_balance):
        text = f"📦 *{product.name}*\n\n"
        if product.description: text += f"📝 {product.description}\n\n"
        text += f"💰 Preço: R$ {product.price:.2f}\n"
        text += f"📦 Estoque: {product.stock} unid.\n"
        text += f"💵 Seu Saldo: R$ {user_balance:.2f}\n"
        text += f"📊 Vendidos: {product.total_sold}\n"
        return text
    
    @staticmethod
    def pix_info(pix_id, amount, expiration, bonus=0):
        text = f"💳 *PIX Gerado*\n\n"
        text += f"💰 Valor: R$ {amount:.2f}\n"
        text += f"🆔 ID: {pix_id}\n"
        text += f"⏰ Expira em: {expiration} min\n"
        if bonus > 0: text += f"🎁 Bônus: R$ {bonus:.2f}\n"
        return text
    
    @staticmethod
    def purchase_confirmation(product_name, amount, email='', password='', purchase_id=''):
        text = f"✅ *Compra Realizada!*\n\n"
        text += f"📦 Produto: {product_name}\n"
        text += f"💰 Valor: R$ {amount:.2f}\n"
        if purchase_id: text += f"🎫 ID: {purchase_id}\n"
        if email: text += f"\n📧 Email: {email}\n🔐 Senha: {password}\n"
        return text
    
    @staticmethod
    def ranking_header(title):
        return f"🏆 *{title}*\n\n"
    
    @staticmethod
    def ranking_item(position, name, value, suffix=''):
        medals = {1: '🥇', 2: '🥈', 3: '🥉'}
        medal = medals.get(position, f'{position}°')
        text = f"{medal} {name} - {value}"
        if suffix: text += f" {suffix}"
        text += "\n"
        return text
    
    @staticmethod
    def divider():
        return "━" * 30
    
    @staticmethod
    def section(title):
        return f"\n{TextFormatter.divider()}\n📋 {title}\n{TextFormatter.divider()}\n"
    
    @staticmethod
    def progress_bar(current, total, length=10):
        filled = int(length * current / total) if total > 0 else 0
        bar = '█' * filled + '░' * (length - filled)
        return f"[{bar}] {current}/{total}"
    
    @staticmethod
    def countdown(minutes):
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0: return f"{hours}h {mins}min"
        return f"{mins}min"
