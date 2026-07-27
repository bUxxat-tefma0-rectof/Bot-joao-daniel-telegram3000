from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import DBManager
from config.settings import ADMIN_ID

db = DBManager()
astates = {}

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Acesso negado!")
        return
    
    s = db.get_stats()
    bot_name = db.get_setting('bot_name', 'BOT')
    
    txt = f"📊 *DASHBOARD @{bot_name}*\n\n"
    txt += f"👥 Usuários: {s['users']}\n"
    txt += f"💰 Receita total: R$ {s['total_revenue']:.2f}\n"
    txt += f"💰 Receita hoje: R$ {s['today_revenue']:.2f}\n"
    txt += f"💰 Receita mês: R$ {s['month_revenue']:.2f}\n"
    txt += f"🛒 Vendas total: {s['sales']}\n"
    txt += f"🛒 Vendas hoje: {s['today_sales']}\n"
    txt += f"📦 Estoque logins: {s['logins_stock']}\n\n"
    txt += f"🤖 Versão: {db.get_setting('bot_version', '1.0.0')}"
    
    kb = [
        [InlineKeyboardButton("⚙️ CONFIGURAÇÕES", callback_data='adm_config')],
        [InlineKeyboardButton("🔧 AÇÕES", callback_data='adm_actions')],
        [InlineKeyboardButton("📊 RELATÓRIOS", callback_data='adm_reports')]
    ]
    
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def adm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    u = q.from_user
    
    if u.id != ADMIN_ID:
        return
    
    # ============ VOLTAR AO DASHBOARD ============
    if d == 'adm_back':
        s = db.get_stats()
        txt = f"📊 *DASHBOARD*\n\n👥 {s['users']} | 💰 R$ {s['total_revenue']:.2f} | 🛒 {s['sales']}"
        kb = [
            [InlineKeyboardButton("⚙️ CONFIGURAÇÕES", callback_data='adm_config')],
            [InlineKeyboardButton("🔧 AÇÕES", callback_data='adm_actions')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ MENU CONFIGURAÇÕES ============
    if d == 'adm_config':
        kb = [
            [InlineKeyboardButton("⚙️ CONFIGURAÇÕES GERAIS", callback_data='adm_cfg_general')],
            [InlineKeyboardButton("👑 CONFIGURAR ADMINS", callback_data='adm_cfg_admins')],
            [InlineKeyboardButton("💼 CONFIGURAR AFILIADOS", callback_data='adm_cfg_affiliate')],
            [InlineKeyboardButton("👥 CONFIGURAR USUÁRIOS", callback_data='adm_cfg_users')],
            [InlineKeyboardButton("💳 CONFIGURAR PIX", callback_data='adm_cfg_pix')],
            [InlineKeyboardButton("📦 CONFIGURAR LOGINS", callback_data='adm_cfg_logins')],
            [InlineKeyboardButton("🔍 CONFIGURAR PESQUISA", callback_data='adm_cfg_search')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_back')]
        ]
        await q.edit_message_text("⚙️ *CONFIGURAÇÕES*", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ CONFIGURAÇÕES GERAIS ============
    if d == 'adm_cfg_general':
        s = db.get_all_settings()
        txt = f"⚙️ *CONFIGURAÇÕES GERAIS*\n\n"
        txt += f"🤖 Nome: @{s.get('bot_name','')}\n"
        txt += f"📞 Suporte: {s.get('support_link','')}\n"
        txt += f"🔧 Manutenção: {s.get('maintenance_mode','off')}\n\n"
        txt += f"*BOTÕES ATUAIS:*\n"
        txt += f"B1: {s.get('btn1_text','')}\n"
        txt += f"B2: {s.get('btn2_text','')}\n"
        txt += f"B3: {s.get('btn3_text','')}\n"
        txt += f"B4: {s.get('btn4_text','')}\n"
        txt += f"B5: {s.get('btn5_text','')}\n"
        txt += f"B6: {s.get('btn6_text','')}\n"
        txt += f"B7: {s.get('btn7_text','')}\n"
        txt += f"B8: {s.get('btn8_text','')}\n"
        txt += f"\n*POSIÇÕES:* {s.get('btn1_pos','')}|{s.get('btn2_pos','')}|{s.get('btn3_pos','')}|{s.get('btn4_pos','')}|{s.get('btn5_pos','')}|{s.get('btn6_pos','')}|{s.get('btn7_pos','')}|{s.get('btn8_pos','')}"
        
        kb = [
            [InlineKeyboardButton("🤖 NOME DO BOT", callback_data='adm_edit_bot_name')],
            [InlineKeyboardButton("📝 TEXTO BOAS-VINDAS", callback_data='adm_edit_welcome')],
            [InlineKeyboardButton("🖼️ IMAGEM INICIAL", callback_data='adm_edit_image')],
            [InlineKeyboardButton("📞 LINK SUPORTE", callback_data='adm_edit_support')],
            [InlineKeyboardButton(f"🔧 MANUTENÇÃO ({s.get('maintenance_mode','off')})", callback_data='adm_toggle_maintenance')],
            [InlineKeyboardButton("━"*15, callback_data='none')],
            [InlineKeyboardButton("📝 TEXTO CATÁLOGO", callback_data='adm_edit_catalog_text')],
            [InlineKeyboardButton("📝 TEXTO PRODUTO", callback_data='adm_edit_product_text')],
            [InlineKeyboardButton("📝 TEXTO SALDO INSUF.", callback_data='adm_edit_insufficient_text')],
            [InlineKeyboardButton("📝 TEXTO PIX RESULTADO", callback_data='adm_edit_pix_result_text')],
            [InlineKeyboardButton("📝 TEXTO PERFIL", callback_data='adm_edit_profile_text')],
            [InlineKeyboardButton("📝 TEXTO RECARGA", callback_data='adm_edit_recarga_text')],
            [InlineKeyboardButton("📝 TEXTO PIX PERGUNTA", callback_data='adm_edit_pix_ask_text')],
            [InlineKeyboardButton("📝 TEXTO MULTI COMPRA", callback_data='adm_edit_multi_text')],
            [InlineKeyboardButton("📝 TEXTO CONVERSÃO", callback_data='adm_edit_convert_text')],
            [InlineKeyboardButton("📝 TEXTO SUCESSO", callback_data='adm_edit_success_text')],
            [InlineKeyboardButton("📝 TEXTO HISTÓRICO", callback_data='adm_edit_history_text')],
            [InlineKeyboardButton("📝 TEXTO TERMOS", callback_data='adm_edit_terms_text')],
            [InlineKeyboardButton("📝 TEXTO SUPORTE", callback_data='adm_edit_support_text')],
            [InlineKeyboardButton("📝 TEXTO FLOOD", callback_data='adm_edit_flood_text')],
            [InlineKeyboardButton("📝 TEXTO PIX EXPIRADO", callback_data='adm_edit_expired_pix_text')],
            [InlineKeyboardButton("━"*15, callback_data='none')],
            [InlineKeyboardButton("🔘 BOTÃO 1", callback_data='adm_edit_btn1'), InlineKeyboardButton("🔘 BOTÃO 2", callback_data='adm_edit_btn2')],
            [InlineKeyboardButton("🔘 BOTÃO 3", callback_data='adm_edit_btn3'), InlineKeyboardButton("🔘 BOTÃO 4", callback_data='adm_edit_btn4')],
            [InlineKeyboardButton("🔘 BOTÃO 5", callback_data='adm_edit_btn5'), InlineKeyboardButton("🔘 BOTÃO 6", callback_data='adm_edit_btn6')],
            [InlineKeyboardButton("🔘 BOTÃO 7", callback_data='adm_edit_btn7'), InlineKeyboardButton("🔘 BOTÃO 8", callback_data='adm_edit_btn8')],
            [InlineKeyboardButton("━"*15, callback_data='none')],
            [InlineKeyboardButton("📐 MUDAR POSIÇÕES", callback_data='adm_edit_pos')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_config')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ CONFIGURAR PIX ============
    if d == 'adm_cfg_pix':
        s = db.get_all_settings()
        token_status = "✅ Configurado" if s.get('mp_access_token') else "❌ Não configurado"
        txt = f"💳 *CONFIGURAR PIX*\n\n"
        txt += f"🔑 Token: {token_status}\n"
        txt += f"📥 Mín: R$ {s.get('deposit_min','2.00')}\n"
        txt += f"📤 Máx: R$ {s.get('deposit_max','150.00')}\n"
        txt += f"⏰ Expira: {s.get('pix_expiration','15')} min\n"
        txt += f"🎁 Bônus: {s.get('bonus_percentage','0')}%\n"
        txt += f"📊 Mín Bônus: R$ {s.get('bonus_min_value','10.00')}"
        
        kb = [
            [InlineKeyboardButton("🔑 MUDAR TOKEN", callback_data='adm_edit_mp_token')],
            [InlineKeyboardButton("📥 MUDAR MÍNIMO", callback_data='adm_edit_deposit_min')],
            [InlineKeyboardButton("📤 MUDAR MÁXIMO", callback_data='adm_edit_deposit_max')],
            [InlineKeyboardButton("⏰ MUDAR EXPIRAÇÃO", callback_data='adm_edit_expiration')],
            [InlineKeyboardButton("🎁 MUDAR BÔNUS", callback_data='adm_edit_bonus')],
            [InlineKeyboardButton("📊 MUDAR MÍN BÔNUS", callback_data='adm_edit_bonus_min')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_config')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ CONFIGURAR LOGINS ============
    if d == 'adm_cfg_logins':
        stock = db.get_stock_count()
        txt = f"📦 *CONFIGURAR LOGINS*\n\n📊 Estoque: {stock} logins\n\n"
        txt += "➕ *ADICIONAR:*\nSERVICO|EMAIL|SENHA|DESCRIÇÃO|DURACAO|PRECO\n\n"
        txt += "➖ *REMOVER:*\nSERVICO (nome do serviço)\n\n"
        txt += "🗑️ *REMOVER PLATAFORMA:*\nEnvie o nome da plataforma\n\n"
        txt += "💣 *ZERAR ESTOQUE:*\nDigite CONFIRMAR\n\n"
        txt += "💰 *MUDAR PREÇO:*\nSERVICO|PRECO"
        
        kb = [
            [InlineKeyboardButton("➕ ADICIONAR LOGIN", callback_data='adm_edit_add_login')],
            [InlineKeyboardButton("➖ REMOVER LOGIN", callback_data='adm_edit_remove_login')],
            [InlineKeyboardButton("🗑️ REMOVER PLATAFORMA", callback_data='adm_edit_remove_platform')],
            [InlineKeyboardButton("💣 ZERAR ESTOQUE", callback_data='adm_edit_clear_stock')],
            [InlineKeyboardButton("💰 MUDAR PREÇO SERVIÇO", callback_data='adm_edit_service_price')],
            [InlineKeyboardButton("💵 MUDAR PREÇO TODOS", callback_data='adm_edit_all_prices')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_config')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ CONFIGURAR AFILIADOS ============
    if d == 'adm_cfg_affiliate':
        s = db.get_all_settings()
        txt = f"💼 *AFILIADOS*\n\n"
        txt += f"Sistema: {s.get('affiliate_system','on')}\n"
        txt += f"Comissão: {s.get('commission_percentage','20')}%\n"
        txt += f"Pontos/Recarga: {s.get('affiliate_points_per_recharge','1')}\n"
        txt += f"Mín Pontos: {s.get('affiliate_min_points','500')}\n"
        txt += f"Multiplicador: {s.get('affiliate_multiplier','0.01')}"
        
        kb = [
            [InlineKeyboardButton(f"SISTEMA ({s.get('affiliate_system','on')})", callback_data='adm_toggle_affiliate')],
            [InlineKeyboardButton("💰 COMISSÃO", callback_data='adm_edit_commission')],
            [InlineKeyboardButton("📥 PONTOS/RECARGA", callback_data='adm_edit_affiliate_points')],
            [InlineKeyboardButton("🎯 MÍN PONTOS", callback_data='adm_edit_affiliate_min_points')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_config')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ CONFIGURAR ADMINS ============
    if d == 'adm_cfg_admins':
        kb = [
            [InlineKeyboardButton("➕ ADICIONAR ADMIN", callback_data='adm_edit_add_admin')],
            [InlineKeyboardButton("➖ REMOVER ADMIN", callback_data='adm_edit_remove_admin')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_config')]
        ]
        await q.edit_message_text("👑 *ADMINS*\n\nAdicione ou remova administradores.", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ CONFIGURAR USUÁRIOS ============
    if d == 'adm_cfg_users':
        s = db.get_all_settings()
        txt = f"👥 *USUÁRIOS*\n\nBônus Registro: R$ {s.get('registration_bonus','0')}\nFlood: {s.get('flood_seconds','6')}s"
        kb = [
            [InlineKeyboardButton("📤 TRANSMITIR", callback_data='adm_edit_broadcast')],
            [InlineKeyboardButton("🔍 PESQUISAR", callback_data='adm_edit_search_user')],
            [InlineKeyboardButton("🎁 BÔNUS REGISTRO", callback_data='adm_edit_registration_bonus')],
            [InlineKeyboardButton("⏱️ FLOOD SEGUNDOS", callback_data='adm_edit_flood_seconds')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_config')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ CONFIGURAR PESQUISA ============
    if d == 'adm_cfg_search':
        kb = [
            [InlineKeyboardButton("📸 ADICIONAR IMAGEM", callback_data='adm_edit_add_image')],
            [InlineKeyboardButton("🗑️ REMOVER IMAGEM", callback_data='adm_edit_remove_image')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_config')]
        ]
        await q.edit_message_text("🔍 *PESQUISA*", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ AÇÕES ============
    if d == 'adm_actions':
        kb = [
            [InlineKeyboardButton("📦 ADICIONAR PRODUTO", callback_data='adm_edit_add_product')],
            [InlineKeyboardButton("✏️ EDITAR PRODUTO", callback_data='adm_edit_edit_product')],
            [InlineKeyboardButton("❌ REMOVER PRODUTO", callback_data='adm_edit_remove_product')],
            [InlineKeyboardButton("📤 TRANSMITIR", callback_data='adm_edit_broadcast')],
            [InlineKeyboardButton("🎁 CRIAR GIFT CARD", callback_data='adm_edit_gift')],
            [InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_back')]
        ]
        await q.edit_message_text("🔧 *AÇÕES*", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ RELATÓRIOS ============
    if d == 'adm_reports':
        s = db.get_stats()
        txt = f"📊 *RELATÓRIOS*\n\n👥 {s['users']} usuários\n💰 R$ {s['total_revenue']:.2f} receita\n🛒 {s['sales']} vendas"
        kb = [[InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_back')]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        return
    
    # ============ TOGGLES ============
    if d == 'adm_toggle_maintenance':
        c = db.get_setting('maintenance_mode', 'off')
        db.set_setting('maintenance_mode', 'on' if c == 'off' else 'off')
        await q.edit_message_text(f"✅ Manutenção {'ATIVADA' if c == 'off' else 'DESATIVADA'}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_cfg_general')]]))
        return
    
    if d == 'adm_toggle_affiliate':
        c = db.get_setting('affiliate_system', 'on')
        db.set_setting('affiliate_system', 'on' if c == 'off' else 'off')
        await q.edit_message_text(f"✅ Afiliado {'ATIVADO' if c == 'off' else 'DESATIVADO'}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 VOLTAR", callback_data='adm_cfg_affiliate')]]))
        return
    
    # ============ EDIÇÕES ============
    if d.startswith('adm_edit_'):
        field = d.replace('adm_edit_', '')
        astates[u.id] = field
        
        prompts = {
            'bot_name': '🤖 Envie o nome do bot (sem @):',
            'welcome': '📝 Envie o texto de boas-vindas:\n\nVariáveis: {id} {saldo} {nome} {username} {indicacoes}',
            'image': '🖼️ Envie a URL da imagem inicial:',
            'support': '📞 Envie o link de suporte:',
            'catalog_text': '📝 Envie o texto do catálogo:\n\nVariáveis: {saldo}',
            'product_text': '📝 Envie o texto do produto:\n\nVariáveis: {nome} {preco} {saldo} {estoque} {descricao} {vendidos} {garantia}',
            'insufficient_text': '📝 Envie o texto de saldo insuficiente:\n\nVariáveis: {saldo} {preco} {falta}',
            'pix_result_text': '📝 Envie o texto do resultado PIX:\n\nVariáveis: {valor} {id} {copia_cola} {saldo} {bonus} {total} {expiracao}',
            'profile_text': '📝 Envie o texto do perfil:\n\nVariáveis: {id} {saldo} {whatsapp} {compras} {gasto} {recarregado} {gifts} {indicacoes} {pontos} {link} {codigo}',
            'recarga_text': '📝 Envie o texto da tela de recarga:\n\nVariáveis: {saldo} {id}',
            'pix_ask_text': '📝 Envie o texto de pergunta do valor PIX:\n\nVariáveis: {min} {max} {bonus} {bonus_min}',
            'multi_text': '📝 Envie o texto de compra múltipla:\n\nVariáveis: {estoque} {nome}',
            'convert_text': '📝 Envie o texto de conversão:\n\nVariáveis: {pontos} {valor} {segundos}',
            'success_text': '📝 Envie o texto de compra aprovada:\n\nVariáveis: {nome} {email} {senha} {id_compra} {data} {vencimento}',
            'history_text': '📝 Envie o texto do histórico:',
            'terms_text': '📝 Envie o texto dos termos de uso:',
            'support_text': '📝 Envie o texto do suporte:',
            'flood_text': '📝 Envie o texto de anti-flood:\n\nVariáveis: {segundos}',
            'expired_pix_text': '📝 Envie o texto de PIX expirado:\n\nVariáveis: {valor} {id}',
            'btn1': '🔘 Envie o texto do Botão 1:',
            'btn2': '🔘 Envie o texto do Botão 2:',
            'btn3': '🔘 Envie o texto do Botão 3:',
            'btn4': '🔘 Envie o texto do Botão 4:',
            'btn5': '🔘 Envie o texto do Botão 5:',
            'btn6': '🔘 Envie o texto do Botão 6:',
            'btn7': '🔘 Envie o texto do Botão 7:',
            'btn8': '🔘 Envie o texto do Botão 8:',
            'pos': '📐 Envie as posições dos 8 botões:\n\nFormato: pos1|pos2|pos3|pos4|pos5|pos6|pos7|pos8\n\nPosições: full, left, right\n\nExemplo:\nfull|full|left|right|left|right|full|full',
            'mp_token': '🔑 Envie o token do Mercado Pago:',
            'deposit_min': '📥 Envie o valor mínimo de depósito:',
            'deposit_max': '📤 Envie o valor máximo de depósito:',
            'expiration': '⏰ Envie o tempo de expiração (minutos):',
            'bonus': '🎁 Envie o percentual de bônus (%):',
            'bonus_min': '📊 Envie o valor mínimo para bônus:',
            'commission': '💰 Envie o percentual de comissão:',
            'affiliate_points': '📥 Envie pontos por recarga:',
            'affiliate_min_points': '🎯 Envie mínimo de pontos para converter:',
            'registration_bonus': '🎁 Envie o bônus de registro:',
            'flood_seconds': '⏱️ Envie os segundos do flood:',
            'convert_seconds': '⏱️ Envie os segundos da conversão:',
            'add_product': '📦 Envie no formato:\nNOME|PREÇO|ESTOQUE|CATEGORIA|DESCRIÇÃO\n\nExemplo:\nNetflix|15.00|50|Streaming|Tela 30 dias',
            'edit_product': '✏️ Envie no formato:\nID_DO_PRODUTO|NOME|PREÇO|ESTOQUE|CATEGORIA|DESCRIÇÃO\n\nExemplo:\n1|Netflix|12.00|60|Filmes|Tela 30 dias',
            'remove_product': '❌ Envie o ID do produto que deseja remover:',
            'broadcast': '📤 Envie a mensagem para transmitir a todos:',
            'gift': '🎁 Envie o valor do Gift Card:\n\nExemplo: 50',
            'add_login': '📦 Envie no formato:\nSERVICO|EMAIL|SENHA|DESCRIÇÃO|DURACAO|PRECO\n\nExemplo:\nNetflix|email@gmail.com|senha123|Tela 30 dias|30 dias|15.00',
            'remove_login': '➖ Envie o nome do serviço para remover:',
            'remove_platform': '🗑️ Envie o nome da plataforma para remover:',
            'clear_stock': '⚠️ Digite CONFIRMAR para zerar todo o estoque:',
            'service_price': '💰 Envie no formato:\nSERVICO|PREÇO\n\nExemplo:\nNetflix|12.00',
            'all_prices': '💵 Envie o novo preço para TODOS os serviços:',
            'add_admin': '➕ Envie o ID Telegram do novo admin:',
            'remove_admin': '➖ Envie o ID Telegram do admin a remover:',
            'search_user': '🔍 Envie o ID Telegram do usuário:',
            'add_image': '📸 Envie a URL da imagem:',
            'remove_image': '🗑️ Envie o nome da imagem a remover:',
        }
        
        msg = prompts.get(field, f'Envie o valor para {field}:')
        
        # Definir botão de cancelar baseado no contexto
        cancel_data = 'adm_cfg_general'
        if field in ['add_product', 'edit_product', 'remove_product', 'broadcast', 'gift', 'add_login', 'remove_login', 'remove_platform', 'clear_stock', 'service_price', 'all_prices']:
            cancel_data = 'adm_actions'
        elif field in ['mp_token', 'deposit_min', 'deposit_max', 'expiration', 'bonus', 'bonus_min']:
            cancel_data = 'adm_cfg_pix'
        
        kb = [[InlineKeyboardButton("🔙 CANCELAR", callback_data=cancel_data)]]
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb))
        return

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    
    if user.id != ADMIN_ID:
        return
    
    if user.id not in astates:
        return
    
    field = astates[user.id]
    
    field_map = {
        'welcome': 'welcome_text', 'image': 'welcome_image', 'support': 'support_link',
        'bot_name': 'bot_name', 'catalog_text': 'catalog_text', 'product_text': 'product_text',
        'insufficient_text': 'insufficient_text', 'pix_result_text': 'pix_result_text',
        'profile_text': 'profile_text', 'recarga_text': 'recarga_text',
        'pix_ask_text': 'pix_ask_text', 'multi_text': 'multi_text',
        'convert_text': 'convert_text', 'success_text': 'success_text',
        'history_text': 'history_text', 'terms_text': 'terms_text',
        'support_text': 'support_text', 'flood_text': 'flood_text',
        'expired_pix_text': 'expired_pix_text',
        'btn1': 'btn1_text', 'btn2': 'btn2_text', 'btn3': 'btn3_text', 'btn4': 'btn4_text',
        'btn5': 'btn5_text', 'btn6': 'btn6_text', 'btn7': 'btn7_text', 'btn8': 'btn8_text',
        'mp_token': 'mp_access_token', 'deposit_min': 'deposit_min',
        'deposit_max': 'deposit_max', 'expiration': 'pix_expiration',
        'bonus': 'bonus_percentage', 'bonus_min': 'bonus_min_value',
        'commission': 'commission_percentage', 'registration_bonus': 'registration_bonus',
        'flood_seconds': 'flood_seconds', 'convert_seconds': 'convert_seconds',
        'affiliate_points': 'affiliate_points_per_recharge',
        'affiliate_min_points': 'affiliate_min_points',
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
            await update.message.reply_text(f"✅ {count} posições salvas com sucesso!")
        
        elif field == 'broadcast':
            from database.models import SessionLocal, User
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
            await update.message.reply_text(f"✅ Transmitido para {count} usuários!")
        
        elif field == 'add_product':
            parts = text.split('|')
            if len(parts) >= 3:
                p = db.add_product(parts[0].strip(), float(parts[1]), int(parts[2]),
                                   parts[3].strip() if len(parts) > 3 else '',
                                   parts[4].strip() if len(parts) > 4 else '')
                await update.message.reply_text(f"✅ Produto '{p.name}' adicionado! ID: {p.id}")
            else:
                await update.message.reply_text("❌ Formato inválido!\nUse: NOME|PREÇO|ESTOQUE|CATEGORIA|DESCRIÇÃO")
        
        elif field == 'edit_product':
            parts = text.split('|')
            if len(parts) >= 3:
                pid = int(parts[0].strip())
                p = db.get_product(pid)
                if p:
                    p.name = parts[1].strip() if len(parts) > 1 else p.name
                    p.price = float(parts[2].strip()) if len(parts) > 2 else p.price
                    p.stock = int(parts[3].strip()) if len(parts) > 3 else p.stock
                    p.category = parts[4].strip() if len(parts) > 4 else p.category
                    p.description = parts[5].strip() if len(parts) > 5 else p.description
                    db.db.commit()
                    await update.message.reply_text(f"✅ Produto ID {pid} editado!\nNome: {p.name}\nPreço: R$ {p.price:.2f}\nEstoque: {p.stock}")
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
                    await update.message.reply_text(f"✅ Produto '{p.name}' removido!")
                else:
                    await update.message.reply_text(f"❌ Produto ID {pid} não encontrado!")
            except:
                await update.message.reply_text("❌ Envie apenas o ID do produto!")
        
        elif field == 'gift':
            try:
                from services.gift_service import GiftService
                gs = GiftService()
                gift = gs.create(float(text))
                await update.message.reply_text(f"✅ Gift Card criado!\n🎁 Código: `{gift.code}`\n💰 Valor: R$ {text}", parse_mode='Markdown')
                gs.close()
            except:
                await update.message.reply_text("❌ Valor inválido!")
        
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
                await update.message.reply_text(f"✅ Login adicionado para {parts[0].strip()}!")
            else:
                await update.message.reply_text("❌ Formato: SERVICO|EMAIL|SENHA|DESCRIÇÃO|DURACAO|PRECO")
        
        elif field == 'remove_login':
            from services.login_service import LoginService
            ls = LoginService()
            count = ls.remove(text.strip())
            ls.close()
            await update.message.reply_text(f"✅ {count} logins removidos!")
        
        elif field == 'remove_platform':
            from services.login_service import LoginService
            ls = LoginService()
            count = ls.remove(text.strip())
            ls.close()
            await update.message.reply_text(f"✅ {count} logins removidos da plataforma!")
        
        elif field == 'clear_stock':
            if text.strip().upper() == 'CONFIRMAR':
                from services.login_service import LoginService
                ls = LoginService()
                count = ls.clear()
                ls.close()
                await update.message.reply_text(f"✅ {count} logins removidos! Estoque zerado!")
            else:
                await update.message.reply_text("❌ Digite CONFIRMAR para zerar o estoque.")
        
        elif field == 'service_price':
            parts = text.split('|')
            if len(parts) >= 2:
                from services.login_service import LoginService
                ls = LoginService()
                count = ls.update_price(parts[0].strip(), float(parts[1].strip()))
                ls.close()
                await update.message.reply_text(f"✅ {count} logins de {parts[0].strip()} atualizados para R$ {parts[1].strip()}!")
            else:
                await update.message.reply_text("❌ Formato: SERVICO|PREÇO")
        
        elif field == 'all_prices':
            try:
                from services.login_service import LoginService
                ls = LoginService()
                count = ls.update_all(float(text))
                ls.close()
                await update.message.reply_text(f"✅ {count} logins atualizados para R$ {text}!")
            except:
                await update.message.reply_text("❌ Valor inválido!")
        
        elif field == 'add_admin':
            try:
                uid = int(text.strip())
                u = db.get_user(uid)
                if u:
                    u.is_admin = True
                    db.db.commit()
                    await update.message.reply_text(f"✅ Admin adicionado: {uid}")
                else:
                    await update.message.reply_text("❌ Usuário não encontrado! Ele precisa iniciar o bot primeiro.")
            except:
                await update.message.reply_text("❌ ID inválido!")
        
        elif field == 'remove_admin':
            try:
                uid = int(text.strip())
                u = db.get_user(uid)
                if u and uid != ADMIN_ID:
                    u.is_admin = False
                    db.db.commit()
                    await update.message.reply_text(f"✅ Admin removido: {uid}")
                else:
                    await update.message.reply_text("❌ Não é possível remover este admin!")
            except:
                await update.message.reply_text("❌ ID inválido!")
        
        elif field == 'search_user':
            try:
                uid = int(text.strip())
                u = db.get_user(uid)
                if u:
                    await update.message.reply_text(
                        f"👤 *Usuário Encontrado*\n\n"
                        f"🆔 ID: {u.telegram_id}\n"
                        f"👤 Nome: {u.first_name or 'N/A'}\n"
                        f"📱 Username: @{u.username or 'N/A'}\n"
                        f"💰 Saldo: R$ {u.balance:.2f}\n"
                        f"💼 Comissão: R$ {u.commission_balance:.2f}\n"
                        f"🛒 Compras: {u.total_purchases}\n"
                        f"💳 Recarregado: R$ {u.total_recharged:.2f}\n"
                        f"🎁 Gifts: {u.gifts_redeemed}\n"
                        f"👥 Indicações: {u.total_referrals}\n"
                        f"⭐ Pontos: {u.affiliate_points}\n"
                        f"📅 Cadastro: {u.created_at.strftime('%d/%m/%Y') if u.created_at else 'N/A'}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("❌ Usuário não encontrado!")
            except:
                await update.message.reply_text("❌ ID inválido!")
        
        elif field in field_map:
            db.set_setting(field_map[field], text)
            await update.message.reply_text(f"✅ Configuração '{field}' salva com sucesso!")
        
        else:
            await update.message.reply_text("✅ Comando processado!")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao salvar: {str(e)}")
    
    finally:
        del astates[user.id]
