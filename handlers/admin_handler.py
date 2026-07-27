from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import DBManager
from config.settings import ADMIN_ID
import json

db = DBManager()
admin_states = {}

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Acesso negado!")
        return
    
    s = db.get_stats()
    txt = f"""
╔══════════════════════════════╗
║     📊 DASHBOARD ADMIN       ║
╚══════════════════════════════╝

👥 Usuários: {s['users']}
📦 Produtos: {s['products']}
📋 Estoque Logins: {s['logins_stock']}

💰 Receita Total: R$ {s['total_revenue']:.2f}
💰 Receita Hoje: R$ {s['today_revenue']:.2f}
💰 Receita Mês: R$ {s['month_revenue']:.2f}

🛒 Vendas Total: {s['sales']}
🛒 Vendas Hoje: {s['today_sales']}
💳 Recargas: {s['total_recharges']}

🤖 @{db.get_setting('bot_name','BOT')}
🔧 v{db.get_setting('bot_version','1.0')}
"""
    
    kb = [
        [InlineKeyboardButton("📝 MENSAGENS E TEXTOS", callback_data='adm_messages')],
        [InlineKeyboardButton("🔘 BOTÕES E MENU", callback_data='adm_buttons')],
        [InlineKeyboardButton("📦 PRODUTOS", callback_data='adm_products')],
        [InlineKeyboardButton("💳 PIX E PAGAMENTOS", callback_data='adm_pix')],
        [InlineKeyboardButton("📋 LOGINS E ESTOQUE", callback_data='adm_logins')],
        [InlineKeyboardButton("👥 USUÁRIOS", callback_data='adm_users')],
        [InlineKeyboardButton("👑 ADMINISTRADORES", callback_data='adm_admins')],
        [InlineKeyboardButton("🔧 SISTEMA", callback_data='adm_system')],
    ]
    
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def adm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    u = q.from_user
    
    if u.id != ADMIN_ID:
        return
    
    # ============ VOLTAR AO MENU PRINCIPAL ============
    if d == 'adm_menu':
        await admin(update, context)
        try: await q.message.delete()
        except: pass
        return
    
    # ============ MENSAGENS E TEXTOS ============
    if d == 'adm_messages':
        s = db.get_all_settings()
        txt = f"""
📝 *MENSAGENS E TEXTOS*

📝 Boas-vindas: {s.get('welcome_text','Não configurado')[:80]}...
📝 Catálogo: {s.get('catalog_text','Não configurado')[:80]}...
📝 Produto: {s.get('product_text','Não configurado')[:80]}...
📝 Saldo Insuf: {s.get('insufficient_text','Não configurado')[:80]}...
📝 PIX Resultado: {s.get('pix_result_text','Não configurado')[:80]}...
📝 Perfil: {s.get('profile_text','Não configurado')[:80]}...
📝 Recarga: {s.get('recarga_text','Não configurado')[:80]}...
📝 Sucesso: {s.get('success_text','Não configurado')[:80]}...
📝 Termos: {s.get('terms_text','Não configurado')[:80]}...
"""
        kb = [
            [InlineKeyboardButton("✏️ EDITAR BOAS-VINDAS", callback_data='adm_edit_welcome')],
            [InlineKeyboardButton("✏️ EDITAR CATÁLOGO", callback_data='adm_edit_catalog_text')],
            [InlineKeyboardButton("✏️ EDITAR PRODUTO", callback_data='adm_edit_product_text')],
            [InlineKeyboardButton("✏️ EDITAR SALDO INSUF", callback_data='adm_edit_insufficient_text')],
            [InlineKeyboardButton("✏️ EDITAR PIX RESULTADO", callback_data='adm_edit_pix_result_text')],
            [InlineKeyboardButton("✏️ EDITAR PERFIL", callback_data='adm_edit_profile_text')],
            [InlineKeyboardButton("✏️ EDITAR RECARGA", callback_data='adm_edit_recarga_text')],
            [InlineKeyboardButton("✏️ EDITAR SUCESSO", callback_data='adm_edit_success_text')],
            [InlineKeyboardButton("✏️ EDITAR TERMOS", callback_data='adm_edit_terms_text')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_menu')],
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ BOTÕES E MENU ============
    if d == 'adm_buttons':
        s = db.get_all_settings()
        txt = f"""
🔘 *BOTÕES E MENU*

*Textos dos Botões:*
1️⃣: {s.get('btn1_text','Vazio')}
2️⃣: {s.get('btn2_text','Vazio')}
3️⃣: {s.get('btn3_text','Vazio')}
4️⃣: {s.get('btn4_text','Vazio')}
5️⃣: {s.get('btn5_text','Vazio')}
6️⃣: {s.get('btn6_text','Vazio')}
7️⃣: {s.get('btn7_text','Vazio')}
8️⃣: {s.get('btn8_text','Vazio')}

*Posições:*
{s.get('btn1_pos','-')}|{s.get('btn2_pos','-')}|{s.get('btn3_pos','-')}|{s.get('btn4_pos','-')}|{s.get('btn5_pos','-')}|{s.get('btn6_pos','-')}|{s.get('btn7_pos','-')}|{s.get('btn8_pos','-')}

🖼️ Imagem: {'✅ Configurada' if s.get('welcome_image') else '❌ Não'}
🤖 Nome: @{s.get('bot_name','')}
📞 Suporte: {s.get('support_link','')}
"""
        kb = [
            [InlineKeyboardButton("1️⃣", callback_data='adm_edit_btn1'), InlineKeyboardButton("2️⃣", callback_data='adm_edit_btn2'), InlineKeyboardButton("3️⃣", callback_data='adm_edit_btn3'), InlineKeyboardButton("4️⃣", callback_data='adm_edit_btn4')],
            [InlineKeyboardButton("5️⃣", callback_data='adm_edit_btn5'), InlineKeyboardButton("6️⃣", callback_data='adm_edit_btn6'), InlineKeyboardButton("7️⃣", callback_data='adm_edit_btn7'), InlineKeyboardButton("8️⃣", callback_data='adm_edit_btn8')],
            [InlineKeyboardButton("📐 MUDAR POSIÇÕES", callback_data='adm_edit_pos')],
            [InlineKeyboardButton("🖼️ MUDAR IMAGEM", callback_data='adm_edit_image')],
            [InlineKeyboardButton("🤖 MUDAR NOME", callback_data='adm_edit_bot_name')],
            [InlineKeyboardButton("📞 MUDAR SUPORTE", callback_data='adm_edit_support')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_menu')],
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ PRODUTOS ============
    if d == 'adm_products':
        products = db.get_products()
        txt = f"📦 *PRODUTOS CADASTRADOS* ({len(products)})\n\n"
        for p in products[:20]:
            txt += f"🆔 {p.id} | {p.name}\n   💰 R$ {p.price:.2f} | 📦 {p.stock} | 🏷️ {p.category}\n\n"
        
        kb = [
            [InlineKeyboardButton("➕ ADICIONAR PRODUTO", callback_data='adm_edit_add_product')],
            [InlineKeyboardButton("✏️ EDITAR PRODUTO", callback_data='adm_edit_edit_product')],
            [InlineKeyboardButton("❌ REMOVER PRODUTO", callback_data='adm_edit_remove_product')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_menu')],
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ PIX ============
    if d == 'adm_pix':
        s = db.get_all_settings()
        token = s.get('mp_access_token','')
        txt = f"""
💳 *CONFIGURAÇÕES PIX*

🔑 Token: {'✅ CONFIGURADO' if token else '❌ NÃO CONFIGURADO'}
📥 Depósito Mínimo: R$ {s.get('deposit_min','2.00')}
📤 Depósito Máximo: R$ {s.get('deposit_max','150.00')}
⏰ Expiração: {s.get('pix_expiration','15')} minutos
🎁 Bônus: {s.get('bonus_percentage','0')}%
📊 Mínimo para Bônus: R$ {s.get('bonus_min_value','10.00')}
"""
        kb = [
            [InlineKeyboardButton("🔑 MUDAR TOKEN", callback_data='adm_edit_mp_token')],
            [InlineKeyboardButton("📥 MUDAR MÍNIMO", callback_data='adm_edit_deposit_min')],
            [InlineKeyboardButton("📤 MUDAR MÁXIMO", callback_data='adm_edit_deposit_max')],
            [InlineKeyboardButton("⏰ MUDAR EXPIRAÇÃO", callback_data='adm_edit_expiration')],
            [InlineKeyboardButton("🎁 MUDAR BÔNUS", callback_data='adm_edit_bonus')],
            [InlineKeyboardButton("📊 MUDAR MÍN BÔNUS", callback_data='adm_edit_bonus_min')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_menu')],
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ LOGINS ============
    if d == 'adm_logins':
        stock = db.get_stock_list()
        txt = f"📦 *ESTOQUE DE LOGINS* ({db.get_stock_count()} total)\n\n"
        for name, qty in stock.items():
            txt += f"📦 {name}: {qty} unid.\n"
        
        kb = [
            [InlineKeyboardButton("➕ ADICIONAR LOGIN", callback_data='adm_edit_add_login')],
            [InlineKeyboardButton("➖ REMOVER LOGIN", callback_data='adm_edit_remove_login')],
            [InlineKeyboardButton("🗑️ REMOVER PLATAFORMA", callback_data='adm_edit_remove_platform')],
            [InlineKeyboardButton("💣 ZERAR ESTOQUE", callback_data='adm_edit_clear_stock')],
            [InlineKeyboardButton("💰 MUDAR PREÇO", callback_data='adm_edit_service_price')],
            [InlineKeyboardButton("💵 MUDAR PREÇO TODOS", callback_data='adm_edit_all_prices')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_menu')],
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ USUÁRIOS ============
    if d == 'adm_users':
        s = db.get_all_settings()
        txt = f"""
👥 *USUÁRIOS*

Total: {db.get_stats()['users']}

🎁 Bônus Registro: R$ {s.get('registration_bonus','0')}
⏱️ Flood: {s.get('flood_seconds','6')} segundos
"""
        kb = [
            [InlineKeyboardButton("🔍 PESQUISAR USUÁRIO", callback_data='adm_edit_search_user')],
            [InlineKeyboardButton("📤 TRANSMITIR", callback_data='adm_edit_broadcast')],
            [InlineKeyboardButton("🎁 MUDAR BÔNUS", callback_data='adm_edit_registration_bonus')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_menu')],
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ ADMINS ============
    if d == 'adm_admins':
        from database.models import SessionLocal, User
        session = SessionLocal()
        admins = session.query(User).filter_by(is_admin=True).all()
        session.close()
        
        txt = f"👑 *ADMINISTRADORES* ({len(admins)})\n\n"
        for a in admins:
            txt += f"👤 {a.first_name or 'N/A'} - ID: {a.telegram_id}\n"
        
        kb = [
            [InlineKeyboardButton("➕ ADICIONAR", callback_data='adm_edit_add_admin')],
            [InlineKeyboardButton("➖ REMOVER", callback_data='adm_edit_remove_admin')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_menu')],
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ SISTEMA ============
    if d == 'adm_system':
        s = db.get_all_settings()
        txt = f"""
🔧 *SISTEMA*

🤖 Nome: @{s.get('bot_name','')}
📱 Versão: {s.get('bot_version','1.0.0')}
🔧 Manutenção: {s.get('maintenance_mode','off')}
📞 Suporte: {s.get('support_link','')}
🔤 Separador: {s.get('separator','===')}
"""
        kb = [
            [InlineKeyboardButton("🤖 NOME DO BOT", callback_data='adm_edit_bot_name')],
            [InlineKeyboardButton(f"🔧 MANUTENÇÃO: {s.get('maintenance_mode','off').upper()}", callback_data='adm_toggle_maintenance')],
            [InlineKeyboardButton("📞 SUPORTE", callback_data='adm_edit_support')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_menu')],
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ TOGGLE MANUTENÇÃO ============
    if d == 'adm_toggle_maintenance':
        c = db.get_setting('maintenance_mode', 'off')
        nv = 'on' if c == 'off' else 'off'
        db.set_setting('maintenance_mode', nv)
        await q.answer(f"✅ Manutenção {'ATIVADA' if nv == 'on' else 'DESATIVADA'}!", show_alert=True)
        return
    
    # ============ EDIÇÕES ============
    if d.startswith('adm_edit_'):
        field = d.replace('adm_edit_', '')
        admin_states[u.id] = field
        
        prompts = {
            'welcome': '📝 Envie o novo texto de BOAS-VINDAS:\n\nVariáveis: {id} {saldo} {nome} {username} {indicacoes}',
            'catalog_text': '📝 Envie o novo texto do CATÁLOGO:\n\nVariáveis: {saldo}',
            'product_text': '📝 Envie o novo texto do PRODUTO:\n\nVariáveis: {nome} {preco} {saldo} {estoque} {descricao} {vendidos} {garantia}',
            'insufficient_text': '📝 Envie o novo texto de SALDO INSUFICIENTE:\n\nVariáveis: {saldo} {preco} {falta}',
            'pix_result_text': '📝 Envie o novo texto do PIX RESULTADO:\n\nVariáveis: {valor} {id} {copia_cola} {saldo} {bonus} {total} {expiracao}',
            'profile_text': '📝 Envie o novo texto do PERFIL:\n\nVariáveis: {id} {saldo} {whatsapp} {compras} {gasto} {recarregado} {gifts} {indicacoes} {pontos} {link} {codigo}',
            'recarga_text': '📝 Envie o novo texto da RECARGA:\n\nVariáveis: {saldo} {id}',
            'success_text': '📝 Envie o novo texto de SUCESSO:\n\nVariáveis: {nome} {email} {senha} {id_compra} {data} {vencimento}',
            'terms_text': '📝 Envie o novo texto dos TERMOS:',
            'btn1': '🔘 Envie o texto do BOTÃO 1:',
            'btn2': '🔘 Envie o texto do BOTÃO 2:',
            'btn3': '🔘 Envie o texto do BOTÃO 3:',
            'btn4': '🔘 Envie o texto do BOTÃO 4:',
            'btn5': '🔘 Envie o texto do BOTÃO 5:',
            'btn6': '🔘 Envie o texto do BOTÃO 6:',
            'btn7': '🔘 Envie o texto do BOTÃO 7:',
            'btn8': '🔘 Envie o texto do BOTÃO 8:',
            'pos': '📐 Envie as 8 posições:\n\nFormato: p1|p2|p3|p4|p5|p6|p7|p8\nPosições: full, left, right\n\nExemplo: full|full|left|right|left|right|full|full',
            'image': '🖼️ Envie a URL da imagem:',
            'bot_name': '🤖 Envie o nome do bot (sem @):',
            'support': '📞 Envie o link de suporte:',
            'mp_token': '🔑 Envie o Token do Mercado Pago:',
            'deposit_min': '📥 Envie o valor MÍNIMO de depósito:',
            'deposit_max': '📤 Envie o valor MÁXIMO de depósito:',
            'expiration': '⏰ Envie o tempo de EXPIRAÇÃO (minutos):',
            'bonus': '🎁 Envie o percentual de BÔNUS (%):',
            'bonus_min': '📊 Envie o valor MÍNIMO para bônus:',
            'registration_bonus': '🎁 Envie o BÔNUS de registro:',
            'add_product': '📦 Envie no formato:\nNOME|PREÇO|ESTOQUE|CATEGORIA|DESCRIÇÃO\n\nEx: Netflix|15.00|50|Streaming|Tela 30 dias',
            'edit_product': '✏️ Envie no formato:\nID|NOME|PREÇO|ESTOQUE|CATEGORIA|DESCRIÇÃO\n\nEx: 1|Netflix|12.00|60|Filmes|Tela 30 dias',
            'remove_product': '❌ Envie o ID do produto para remover:',
            'broadcast': '📤 Envie a mensagem para TODOS os usuários:',
            'search_user': '🔍 Envie o ID Telegram do usuário:',
            'add_admin': '➕ Envie o ID Telegram do novo admin:',
            'remove_admin': '➖ Envie o ID Telegram do admin a remover:',
            'add_login': '📦 Envie no formato:\nSERVICO|EMAIL|SENHA|DESCRIÇÃO|DURACAO|PRECO\n\nEx: Netflix|email@gmail.com|senha123|Tela 30 dias|30 dias|15.00',
            'remove_login': '➖ Envie o nome do SERVIÇO para remover:',
            'remove_platform': '🗑️ Envie o nome da PLATAFORMA para remover:',
            'clear_stock': '⚠️ Digite CONFIRMAR para zerar TODO o estoque:',
            'service_price': '💰 Envie no formato:\nSERVICO|PREÇO\n\nEx: Netflix|12.00',
            'all_prices': '💵 Envie o novo preço para TODOS:',
        }
        
        msg = prompts.get(field, f'Envie o valor para {field}:')
        kb = [[InlineKeyboardButton("🔙 CANCELAR", callback_data='adm_menu')]]
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb))
        return

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    
    if user.id != ADMIN_ID:
        return
    
    if user.id not in admin_states:
        return
    
    field = admin_states[user.id]
    
    field_map = {
        'welcome': 'welcome_text', 'catalog_text': 'catalog_text', 'product_text': 'product_text',
        'insufficient_text': 'insufficient_text', 'pix_result_text': 'pix_result_text',
        'profile_text': 'profile_text', 'recarga_text': 'recarga_text',
        'success_text': 'success_text', 'terms_text': 'terms_text',
        'btn1': 'btn1_text', 'btn2': 'btn2_text', 'btn3': 'btn3_text', 'btn4': 'btn4_text',
        'btn5': 'btn5_text', 'btn6': 'btn6_text', 'btn7': 'btn7_text', 'btn8': 'btn8_text',
        'image': 'welcome_image', 'bot_name': 'bot_name', 'support': 'support_link',
        'mp_token': 'mp_access_token', 'deposit_min': 'deposit_min', 'deposit_max': 'deposit_max',
        'expiration': 'pix_expiration', 'bonus': 'bonus_percentage', 'bonus_min': 'bonus_min_value',
        'registration_bonus': 'registration_bonus',
    }
    
    try:
        if field == 'pos':
            parts = text.split('|')
            count = 0
            for i, p in enumerate(parts[:8], 1):
                p = p.strip()
                if p in ['full', 'left', 'right']:
                    db.set_setting(f'btn{i}_pos', p)
                    count += 1
            await update.message.reply_text(f"✅ {count} POSIÇÕES SALVAS COM SUCESSO!")
        
        elif field == 'add_product':
            parts = text.split('|')
            if len(parts) >= 3:
                p = db.add_product(parts[0].strip(), float(parts[1]), int(parts[2]),
                                   parts[3].strip() if len(parts) > 3 else '',
                                   parts[4].strip() if len(parts) > 4 else '')
                await update.message.reply_text(f"✅ PRODUTO ADICIONADO COM SUCESSO!\n\n📦 Nome: {p.name}\n💰 Preço: R$ {p.price:.2f}\n📦 Estoque: {p.stock}\n🏷️ Categoria: {p.category}\n🆔 ID: {p.id}")
            else:
                await update.message.reply_text("❌ Formato inválido!\nUse: NOME|PREÇO|ESTOQUE|CATEGORIA|DESCRIÇÃO")
        
        elif field == 'edit_product':
            parts = text.split('|')
            if len(parts) >= 2:
                pid = int(parts[0].strip())
                p = db.get_product(pid)
                if p:
                    old_name = p.name
                    old_price = p.price
                    if len(parts) > 1 and parts[1].strip(): p.name = parts[1].strip()
                    if len(parts) > 2 and parts[2].strip(): p.price = float(parts[2].strip())
                    if len(parts) > 3 and parts[3].strip(): p.stock = int(parts[3].strip())
                    if len(parts) > 4 and parts[4].strip(): p.category = parts[4].strip()
                    if len(parts) > 5 and parts[5].strip(): p.description = parts[5].strip()
                    db.db.commit()
                    await update.message.reply_text(f"✅ PRODUTO EDITADO COM SUCESSO!\n\n🆔 ID: {pid}\n📦 Nome: {p.name}\n💰 Preço: R$ {p.price:.2f}\n📦 Estoque: {p.stock}\n🏷️ Categoria: {p.category}")
                else:
                    await update.message.reply_text(f"❌ Produto ID {pid} não encontrado!")
            else:
                await update.message.reply_text("❌ Formato: ID|NOME|PREÇO|ESTOQUE|CATEGORIA|DESCRIÇÃO")
        
        elif field == 'remove_product':
            try:
                pid = int(text.strip())
                p = db.get_product(pid)
                if p:
                    db.delete_product(pid)
                    await update.message.reply_text(f"✅ PRODUTO REMOVIDO COM SUCESSO!\n\n📦 {p.name} (ID: {pid})")
                else:
                    await update.message.reply_text(f"❌ Produto ID {pid} não encontrado!")
            except:
                await update.message.reply_text("❌ Envie apenas o número do ID!")
        
        elif field == 'broadcast':
            from database.models import SessionLocal, User
            session = SessionLocal()
            users = session.query(User).all()
            count = 0
            await update.message.reply_text(f"📤 Enviando para {len(users)} usuários...")
            for u in users:
                try:
                    await context.bot.send_message(u.telegram_id, text)
                    count += 1
                except: pass
            session.close()
            await update.message.reply_text(f"✅ TRANSMISSÃO CONCLUÍDA!\n📤 Enviado: {count}\n❌ Falhas: {len(users)-count}")
        
        elif field == 'search_user':
            try:
                uid = int(text.strip())
                u = db.get_user(uid)
                if u:
                    await update.message.reply_text(
                        f"✅ USUÁRIO ENCONTRADO!\n\n"
                        f"🆔 ID: {u.telegram_id}\n"
                        f"👤 Nome: {u.first_name or 'N/A'}\n"
                        f"📱 @{u.username or 'N/A'}\n"
                        f"💰 Saldo: R$ {u.balance:.2f}\n"
                        f"🛒 Compras: {u.total_purchases}\n"
                        f"💳 Recarregado: R$ {u.total_recharged:.2f}\n"
                        f"📅 Desde: {u.created_at.strftime('%d/%m/%Y') if u.created_at else 'N/A'}"
                    )
                else:
                    await update.message.reply_text("❌ Usuário não encontrado!")
            except:
                await update.message.reply_text("❌ ID inválido!")
        
        elif field == 'add_admin':
            try:
                uid = int(text.strip())
                u = db.get_user(uid)
                if u:
                    u.is_admin = True
                    db.db.commit()
                    await update.message.reply_text(f"✅ ADMIN ADICIONADO!\n👤 ID: {uid}")
                else:
                    await update.message.reply_text("❌ Usuário não encontrado!")
            except:
                await update.message.reply_text("❌ ID inválido!")
        
        elif field == 'remove_admin':
            try:
                uid = int(text.strip())
                if uid == ADMIN_ID:
                    await update.message.reply_text("❌ Você não pode remover a si mesmo!")
                    return
                u = db.get_user(uid)
                if u:
                    u.is_admin = False
                    db.db.commit()
                    await update.message.reply_text(f"✅ ADMIN REMOVIDO!\n👤 ID: {uid}")
                else:
                    await update.message.reply_text("❌ Usuário não encontrado!")
            except:
                await update.message.reply_text("❌ ID inválido!")
        
        elif field == 'add_login':
            parts = text.split('|')
            if len(parts) >= 3:
                from services.login_service import LoginService
                ls = LoginService()
                ls.add(parts[0].strip(), parts[1].strip(), parts[2].strip(),
                       parts[3].strip() if len(parts) > 3 else '',
                       parts[4].strip() if len(parts) > 4 else '30 dias',
                       float(parts[5]) if len(parts) > 5 else 0)
                ls.close()
                await update.message.reply_text(f"✅ LOGIN ADICIONADO!\n📦 Serviço: {parts[0].strip()}")
            else:
                await update.message.reply_text("❌ Formato: SERVICO|EMAIL|SENHA|DESCRIÇÃO|DURACAO|PRECO")
        
        elif field == 'remove_login':
            from services.login_service import LoginService
            ls = LoginService()
            count = ls.remove(text.strip())
            ls.close()
            await update.message.reply_text(f"✅ {count} LOGINS REMOVIDOS!")
        
        elif field == 'remove_platform':
            from services.login_service import LoginService
            ls = LoginService()
            count = ls.remove(text.strip())
            ls.close()
            await update.message.reply_text(f"✅ {count} LOGINS REMOVIDOS da plataforma!")
        
        elif field == 'clear_stock':
            if text.strip().upper() == 'CONFIRMAR':
                from services.login_service import LoginService
                ls = LoginService()
                count = ls.clear()
                ls.close()
                await update.message.reply_text(f"✅ ESTOQUE ZERADO! {count} logins removidos.")
            else:
                await update.message.reply_text("❌ Digite CONFIRMAR para zerar o estoque.")
        
        elif field == 'service_price':
            parts = text.split('|')
            if len(parts) >= 2:
                from services.login_service import LoginService
                ls = LoginService()
                count = ls.update_price(parts[0].strip(), float(parts[1].strip()))
                ls.close()
                await update.message.reply_text(f"✅ {count} LOGINS ATUALIZADOS!\n💰 {parts[0].strip()}: R$ {parts[1].strip()}")
            else:
                await update.message.reply_text("❌ Formato: SERVICO|PREÇO")
        
        elif field == 'all_prices':
            try:
                from services.login_service import LoginService
                ls = LoginService()
                count = ls.update_all(float(text))
                ls.close()
                await update.message.reply_text(f"✅ {count} LOGINS ATUALIZADOS para R$ {text}!")
            except:
                await update.message.reply_text("❌ Valor inválido!")
        
        elif field == 'gift':
            try:
                from services.gift_service import GiftService
                gs = GiftService()
                gift = gs.create(float(text))
                await update.message.reply_text(f"✅ GIFT CARD CRIADO!\n🎁 Código: `{gift.code}`\n💰 Valor: R$ {text}", parse_mode='Markdown')
                gs.close()
            except:
                await update.message.reply_text("❌ Valor inválido!")
        
        elif field in field_map:
            db.set_setting(field_map[field], text)
            await update.message.reply_text(f"✅ CONFIGURAÇÃO SALVA COM SUCESSO!\n🔧 {field}")
        
        else:
            await update.message.reply_text("✅ COMANDO PROCESSADO!")
    
    except Exception as e:
        await update.message.reply_text(f"❌ ERRO AO SALVAR: {str(e)}")
    
    finally:
        del admin_states[user.id]
