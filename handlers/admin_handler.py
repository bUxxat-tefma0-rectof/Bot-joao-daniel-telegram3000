from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager
from config.settings import ADMIN_ID

db = DBManager()
astates = {}

async def admin(update, context):
    if update.effective_user.id != ADMIN_ID: await update.message.reply_text("❌"); return
    s = db.get_stats()
    bot_name = db.get_setting('bot_name', 'STORE BOT')
    txt = f"📊 Dashboard @{bot_name}\n\n👥 Users: {s['users']}\n💰 Receita: R$ {s['total_revenue']:.2f}\n💰 Mês: R$ {s['month_revenue']:.2f}\n💰 Hoje: R$ {s['today_revenue']:.2f}\n🛒 Vendas: {s['sales']}\n🛒 Hoje: {s['today_sales']}\n📦 Estoque: {s['logins_stock']}"
    kb = [
        [InlineKeyboardButton("⚙️ Configurações", callback_data='adm_config')],
        [InlineKeyboardButton("🔧 Ações", callback_data='adm_actions')],
        [InlineKeyboardButton("📊 Transações", callback_data='adm_transactions')],
        [InlineKeyboardButton("🔄 Atualizações", callback_data='adm_updates')]
    ]
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def adm_callback(update, context):
    q = update.callback_query; await q.answer(); d = q.data; u = q.from_user
    if u.id != ADMIN_ID: return
    
    if d == 'adm_config':
        kb = [
            [InlineKeyboardButton("⚙️ Configurações Gerais", callback_data='adm_cfg_general')],
            [InlineKeyboardButton("👑 Configurar Admins", callback_data='adm_cfg_admins')],
            [InlineKeyboardButton("💼 Configurar Afiliados", callback_data='adm_cfg_affiliate')],
            [InlineKeyboardButton("👥 Configurar Usuários", callback_data='adm_cfg_users')],
            [InlineKeyboardButton("💳 Configurar PIX", callback_data='adm_cfg_pix')],
            [InlineKeyboardButton("📦 Configurar Logins", callback_data='adm_cfg_logins')],
            [InlineKeyboardButton("🔍 Configurar Pesquisa", callback_data='adm_cfg_search')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='adm_back')]
        ]
        await q.edit_message_text("⚙️ Configurações", reply_markup=InlineKeyboardMarkup(kb))
    
    elif d == 'adm_cfg_general':
        s = db.get_all_settings()
        txt = f"⚙️ Gerais\n\nNome: @{s.get('bot_name', 'STORE BOT')}\nSuporte: {s.get('support_link', '')}\nManutenção: {s.get('maintenance_mode', 'off')}"
        kb = [
            [InlineKeyboardButton("📝 Nome do Bot", callback_data='adm_edit_bot_name')],
            [InlineKeyboardButton("📝 Texto Boas-vindas", callback_data='adm_edit_welcome')],
            [InlineKeyboardButton("🖼️ Imagem", callback_data='adm_edit_image')],
            [InlineKeyboardButton("📞 Suporte", callback_data='adm_edit_support')],
            [InlineKeyboardButton(f"🔧 Manutenção ({s.get('maintenance_mode', 'off')})", callback_data='adm_toggle_maintenance')],
            [InlineKeyboardButton("📝 Texto Catálogo", callback_data='adm_edit_catalog_text')],
            [InlineKeyboardButton("📝 Texto Produto", callback_data='adm_edit_product_text')],
            [InlineKeyboardButton("📝 Texto Saldo Insuf.", callback_data='adm_edit_insufficient_text')],
            [InlineKeyboardButton("📝 Texto PIX Resultado", callback_data='adm_edit_pix_result_text')],
            [InlineKeyboardButton("📝 Texto Perfil", callback_data='adm_edit_profile_text')],
            [InlineKeyboardButton("📝 Texto Recarga", callback_data='adm_edit_recarga_text')],
            [InlineKeyboardButton("📝 Texto PIX Pergunta", callback_data='adm_edit_pix_ask_text')],
            [InlineKeyboardButton("📝 Texto Multi Compra", callback_data='adm_edit_multi_text')],
            [InlineKeyboardButton("📝 Texto Conversão", callback_data='adm_edit_convert_text')],
            [InlineKeyboardButton("📝 Texto Sucesso", callback_data='adm_edit_success_text')],
            [InlineKeyboardButton("📝 Texto Histórico", callback_data='adm_edit_history_text')],
            [InlineKeyboardButton("📝 Texto Termos", callback_data='adm_edit_terms_text')],
            [InlineKeyboardButton("📝 Texto Suporte", callback_data='adm_edit_support_text')],
            [InlineKeyboardButton("📝 Texto Flood", callback_data='adm_edit_flood_text')],
            [InlineKeyboardButton("📝 Texto PIX Expirado", callback_data='adm_edit_expired_pix_text')],
            [InlineKeyboardButton("🔘 B1", callback_data='adm_edit_btn1'), InlineKeyboardButton("🔘 B2", callback_data='adm_edit_btn2')],
            [InlineKeyboardButton("🔘 B3", callback_data='adm_edit_btn3'), InlineKeyboardButton("🔘 B4", callback_data='adm_edit_btn4')],
            [InlineKeyboardButton("🔘 B5", callback_data='adm_edit_btn5'), InlineKeyboardButton("🔘 B6", callback_data='adm_edit_btn6')],
            [InlineKeyboardButton("🔘 B7", callback_data='adm_edit_btn7'), InlineKeyboardButton("🔘 B8", callback_data='adm_edit_btn8')],
            [InlineKeyboardButton("📐 Posições", callback_data='adm_edit_pos')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='adm_config')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    
    elif d == 'adm_cfg_pix':
        s = db.get_all_settings()
        txt = f"💳 PIX\n\nToken: {'✅' if s.get('mp_access_token') else '❌'}\nMín: R$ {s.get('deposit_min', '')}\nMáx: R$ {s.get('deposit_max', '')}\nExpira: {s.get('pix_expiration', '')}min\nBônus: {s.get('bonus_percentage', '')}%\nMín Bônus: R$ {s.get('bonus_min_value', '')}"
        kb = [
            [InlineKeyboardButton("🔑 Token", callback_data='adm_edit_mp_token')],
            [InlineKeyboardButton("📥 Mín", callback_data='adm_edit_deposit_min')],
            [InlineKeyboardButton("📤 Máx", callback_data='adm_edit_deposit_max')],
            [InlineKeyboardButton("⏰ Expira", callback_data='adm_edit_expiration')],
            [InlineKeyboardButton("🎁 Bônus", callback_data='adm_edit_bonus')],
            [InlineKeyboardButton("📊 Mín Bônus", callback_data='adm_edit_bonus_min')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='adm_config')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    
    elif d == 'adm_cfg_logins':
        txt = f"📦 Logins\n\nEstoque: {db.get_stock_count()}"
        kb = [
            [InlineKeyboardButton("➕ Adicionar", callback_data='adm_edit_add_login')],
            [InlineKeyboardButton("➖ Remover", callback_data='adm_edit_remove_login')],
            [InlineKeyboardButton("🗑️ Remover Plataforma", callback_data='adm_edit_remove_platform')],
            [InlineKeyboardButton("💣 Zerar Estoque", callback_data='adm_edit_clear_stock')],
            [InlineKeyboardButton("💰 Mudar Preço Serviço", callback_data='adm_edit_service_price')],
            [InlineKeyboardButton("💵 Mudar Preço Todos", callback_data='adm_edit_all_prices')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='adm_config')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    
    elif d == 'adm_cfg_affiliate':
        s = db.get_all_settings()
        txt = f"💼 Afiliados\n\nSistema: {s.get('affiliate_system', 'on')}\nComissão: {s.get('commission_percentage', '')}%\nPontos/Recarga: {s.get('affiliate_points_per_recharge', '')}\nMín Pontos: {s.get('affiliate_min_points', '')}\nMultiplicador: {s.get('affiliate_multiplier', '')}"
        kb = [
            [InlineKeyboardButton(f"Sistema ({s.get('affiliate_system', 'on')})", callback_data='adm_toggle_affiliate')],
            [InlineKeyboardButton("💰 Comissão", callback_data='adm_edit_commission')],
            [InlineKeyboardButton("📥 Pontos/Recarga", callback_data='adm_edit_affiliate_points')],
            [InlineKeyboardButton("🎯 Mín Pontos", callback_data='adm_edit_affiliate_min_points')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='adm_config')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    
    elif d == 'adm_cfg_users':
        s = db.get_all_settings()
        txt = f"👥 Usuários\n\nBônus Registro: R$ {s.get('registration_bonus', '')}\nFlood: {s.get('flood_seconds', '')}s"
        kb = [
            [InlineKeyboardButton("📤 Transmitir", callback_data='adm_edit_broadcast')],
            [InlineKeyboardButton("🔍 Pesquisar", callback_data='adm_edit_search_user')],
            [InlineKeyboardButton("🎁 Bônus Registro", callback_data='adm_edit_registration_bonus')],
            [InlineKeyboardButton("⏱️ Flood Segundos", callback_data='adm_edit_flood_seconds')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='adm_config')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    
    elif d == 'adm_cfg_admins':
        kb = [
            [InlineKeyboardButton("➕ Adicionar", callback_data='adm_edit_add_admin')],
            [InlineKeyboardButton("➖ Remover", callback_data='adm_edit_remove_admin')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='adm_config')]
        ]
        await q.edit_message_text("👑 Admins", reply_markup=InlineKeyboardMarkup(kb))
    
    elif d == 'adm_cfg_search':
        kb = [
            [InlineKeyboardButton("📸 Adicionar Imagem", callback_data='adm_edit_add_image')],
            [InlineKeyboardButton("🗑️ Remover Imagem", callback_data='adm_edit_remove_image')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='adm_config')]
        ]
        await q.edit_message_text("🔍 Pesquisa", reply_markup=InlineKeyboardMarkup(kb))
    
    elif d == 'adm_actions':
        kb = [
            [InlineKeyboardButton("📦 Adicionar Produto", callback_data='adm_edit_add_product')],
            [InlineKeyboardButton("📤 Transmitir", callback_data='adm_edit_broadcast')],
            [InlineKeyboardButton("🎁 Criar Gift Card", callback_data='adm_edit_gift')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='adm_back')]
        ]
        await q.edit_message_text("🔧 Ações", reply_markup=InlineKeyboardMarkup(kb))
    
    elif d == 'adm_transactions':
        s = db.get_stats()
        await q.edit_message_text(f"📊 Transações\n\nVendas: {s['sales']}\nReceita: R$ {s['total_revenue']:.2f}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Voltar", callback_data='adm_back')]]))
    
    elif d == 'adm_updates':
        await q.edit_message_text(f"🔄 Versão: {db.get_setting('bot_version', '1.0.0')}\n✅ Sistema operacional", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Voltar", callback_data='adm_back')]]))
    
    elif d == 'adm_back':
        s = db.get_stats()
        bot_name = db.get_setting('bot_name', 'STORE BOT')
        txt = f"📊 Dashboard @{bot_name}\n\n👥 {s['users']}\n💰 R$ {s['total_revenue']:.2f}"
        kb = [[InlineKeyboardButton("⚙️ Configurações", callback_data='adm_config')], [InlineKeyboardButton("🔧 Ações", callback_data='adm_actions')]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    
    elif d == 'adm_toggle_maintenance':
        c = db.get_setting('maintenance_mode', 'off'); db.set_setting('maintenance_mode', 'on' if c == 'off' else 'off')
        await q.edit_message_text(f"✅ {'ATIVADA' if c == 'off' else 'DESATIVADA'}")
    
    elif d == 'adm_toggle_affiliate':
        c = db.get_setting('affiliate_system', 'on'); db.set_setting('affiliate_system', 'on' if c == 'off' else 'off')
        await q.edit_message_text(f"✅ {'ATIVADO' if c == 'off' else 'DESATIVADO'}")
    
    elif d.startswith('adm_edit_'):
        field = d.replace('adm_edit_', '')
        astates[u.id] = field
        prompts = {
            'bot_name': '📝 Nome do Bot (sem @):',
            'welcome': '📝 Texto Boas-vindas:', 'image': '🖼️ URL Imagem:', 'support': '📞 Suporte:',
            'catalog_text': '📝 Texto Catálogo:', 'product_text': '📝 Texto Produto:', 'insufficient_text': '📝 Texto Saldo Insuf.:',
            'pix_result_text': '📝 Texto PIX Resultado:', 'profile_text': '📝 Texto Perfil:', 'recarga_text': '📝 Texto Recarga:',
            'pix_ask_text': '📝 Texto PIX Pergunta:', 'multi_text': '📝 Texto Multi Compra:', 'convert_text': '📝 Texto Conversão:',
            'success_text': '📝 Texto Sucesso:', 'history_text': '📝 Texto Histórico:', 'terms_text': '📝 Texto Termos:',
            'support_text': '📝 Texto Suporte:', 'flood_text': '📝 Texto Flood:', 'expired_pix_text': '📝 Texto PIX Expirado:',
            'btn1': '🔘 Botão 1:', 'btn2': '🔘 Botão 2:', 'btn3': '🔘 Botão 3:', 'btn4': '🔘 Botão 4:',
            'btn5': '🔘 Botão 5:', 'btn6': '🔘 Botão 6:', 'btn7': '🔘 Botão 7:', 'btn8': '🔘 Botão 8:',
            'pos': '📐 Posições (8):\nfull|left|right|full|left|right|left|right',
            'mp_token': '🔑 Token MP:', 'deposit_min': '📥 Mín:', 'deposit_max': '📤 Máx:', 'expiration': '⏰ Expira (min):',
            'bonus': '🎁 Bônus (%):', 'bonus_min': '📊 Mín Bônus:', 'commission': '💰 Comissão (%):',
            'affiliate_points': '📥 Pontos/Recarga:', 'affiliate_min_points': '🎯 Mín Pontos:',
            'registration_bonus': '🎁 Bônus Registro:', 'flood_seconds': '⏱️ Flood Segundos:',
            'add_login': '📦 SERVICO|EMAIL|SENHA|DESC|DURACAO|PRECO:', 'remove_login': '➖ SERVICO:',
            'remove_platform': '🗑️ Plataforma:', 'clear_stock': '💣 Digite CONFIRMAR:',
            'service_price': '💰 SERVICO|PRECO:', 'all_prices': '💵 Preço:',
            'add_product': '📦 NOME|PREÇO|ESTOQUE|CATEGORIA:', 'broadcast': '📤 Mensagem:',
            'gift': '🎁 Valor:', 'add_admin': '➕ ID:', 'remove_admin': '➖ ID:',
            'search_user': '🔍 ID:', 'add_image': '📸 URL:', 'remove_image': '🗑️ Nome:',
        }
        await q.edit_message_text(prompts.get(field, f'Envie {field}:'))
