from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager
from services.pix_service import PixService
from services.login_service import LoginService
from services.affiliate_service import AffiliateService
from services.pdf_service import PDFService

db = DBManager()
waiting = {}
selected = {}

def build_kb():
    p = [db.get_setting(f'btn{i}_pos', 'full') for i in range(1, 9)]
    b = [db.get_setting(f'btn{i}_text', '') for i in range(1, 9)]
    kb = []
    if b[0]: kb.append([InlineKeyboardButton(b[0], callback_data='m1')])
    r2 = []
    if p[1] in ['left', 'full'] and b[1]: r2.append(InlineKeyboardButton(b[1], callback_data='m2'))
    if p[2] in ['right', 'full'] and b[2]: r2.append(InlineKeyboardButton(b[2], callback_data='m3'))
    if r2: kb.append(r2)
    r3 = []
    if p[3] in ['left', 'full'] and b[3]: r3.append(InlineKeyboardButton(b[3], callback_data='m4'))
    if p[4] in ['right', 'full'] and b[4]: r3.append(InlineKeyboardButton(b[4], callback_data='m5'))
    if r3: kb.append(r3)
    if b[5]: kb.append([InlineKeyboardButton(b[5], callback_data='m6')])
    if b[6]: kb.append([InlineKeyboardButton(b[6], callback_data='m7')])
    if b[7]: kb.append([InlineKeyboardButton(b[7], callback_data='m8')])
    return kb

async def start(update, context):
    u = update.effective_user
    du = db.get_user(u.id) or db.create_user(u.id, u.username, u.first_name)
    w = db.get_setting('welcome_text', '')
    w = w.replace('{id}', str(u.id)).replace('{saldo}', f'R$ {du.balance:.2f}').replace('{nome}', u.first_name or '').replace('{username}', f'@{u.username}' if u.username else '').replace('{indicacoes}', str(du.total_referrals))
    img = db.get_setting('welcome_image', '')
    kb = build_kb()
    reply = InlineKeyboardMarkup(kb)
    if img:
        try: await update.message.reply_photo(photo=img, caption=w, reply_markup=reply)
        except: await update.message.reply_text(w, reply_markup=reply)
    else: await update.message.reply_text(w, reply_markup=reply)

async def callback(update, context):
    q = update.callback_query; await q.answer(); d = q.data; u = q.from_user
    du = db.get_user(u.id); bal = du.balance if du else 0
    
    # ============ CATÁLOGO (m1) ============
    if d == 'm1':
        prods = db.get_products()
        cats = list(set(p.category for p in prods if p.category))
        txt = db.get_setting('catalog_text', '')
        txt = txt.replace('{saldo}', f'R$ {bal:.2f}')
        kb = []
        
        if cats:
            cat_counts = {}
            for p in prods:
                if p.category not in cat_counts:
                    cat_counts[p.category] = 0
                cat_counts[p.category] += 1
            
            for c in cats:
                count = cat_counts.get(c, 0)
                kb.append([InlineKeyboardButton(f"{c} ({count})", callback_data=f'cat_{c}')])
        else:
            for p in prods:
                kb.append([InlineKeyboardButton(f"{p.name} - R$ {p.price:.2f}", callback_data=f'prod_{p.id}')])
        
        kb.append([InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='back')])
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    
    # ============ CATEGORIA ============
    elif d.startswith('cat_'):
        cat = d.replace('cat_', '')
        prods = db.get_products(cat)
        txt = db.get_setting('catalog_text', '')
        txt = txt.replace('{saldo}', f'R$ {bal:.2f}')
        kb = [[InlineKeyboardButton(f"{p.name} - R$ {p.price:.2f}", callback_data=f'prod_{p.id}')] for p in prods]
        kb.append([InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='m1')])
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    
    # ============ PRODUTO ============
    elif d.startswith('prod_'):
        pid = int(d.replace('prod_', ''))
        p = db.get_product(pid)
        if not p: return
        txt = db.get_setting('product_text', '')
        txt = txt.replace('{nome}', p.name).replace('{preco}', f'R$ {p.price:.2f}').replace('{saldo}', f'R$ {bal:.2f}').replace('{estoque}', str(p.stock)).replace('{descricao}', p.description or '').replace('{vendidos}', str(p.total_sold)).replace('{garantia}', p.warranty or '')
        selected[u.id] = pid
        kb = []
        if p.stock > 0:
            kb.append([InlineKeyboardButton(db.get_setting('buy_btn', '💳 Comprar'), callback_data=f'buy_{pid}')])
            kb.append([InlineKeyboardButton(db.get_setting('multi_btn', '🛒 Comprar Qtd'), callback_data=f'multi_{pid}')])
        kb.append([InlineKeyboardButton(db.get_setting('add_saldo_btn', '💰 Add Saldo'), callback_data='m3')])
        kb.append([InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data=f'cat_{p.category}')])
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    
    # ============ COMPRAR ============
    elif d.startswith('buy_'):
        pid = int(d.replace('buy_', ''))
        p = db.get_product(pid)
        if not p: return
        if bal < p.price:
            falta = p.price - bal
            txt = db.get_setting('insufficient_text', '')
            txt = txt.replace('{saldo}', f'R$ {bal:.2f}').replace('{preco}', f'R$ {p.price:.2f}').replace('{falta}', f'R$ {falta:.2f}')
            kb = [
                [InlineKeyboardButton(db.get_setting('pix_btn', '💠 Gerar PIX').replace('{valor}', f'R$ {p.price:.2f}'), callback_data=f'pixbuy_{p.price}')],
                [InlineKeyboardButton(db.get_setting('cancel_btn', '❌ Cancelar'), callback_data=f'prod_{pid}')]
            ]
            await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
            return
        if p.stock <= 0: await q.edit_message_text("❌ Esgotado!"); return
        
        db.subtract_balance(u.id, p.price)
        db.decrease_stock(pid)
        ls = LoginService()
        login = ls.get(p.name)
        email = login.email if login else ''
        pw = login.password if login else ''
        if login: ls.sold(login.id, u.id)
        pur = db.create_purchase(u.id, p.name, p.price, email, pw, '')
        ls.close()
        af = AffiliateService()
        af.add_commission(u.id, p.price)
        af.close()
        
        user_data = {'id': str(u.id), 'nome': u.first_name or '', 'saldo': db.get_balance(u.id)}
        receipt_pdf = PDFService.generate_purchase_receipt(user_data, pur)
        await q.message.reply_document(document=receipt_pdf, filename=f'compra_{pur.purchase_id[:8]}.pdf', caption="📄 Comprovante")
        
        txt = db.get_setting('success_text', '✅ Compra realizada!')
        txt = txt.replace('{nome}', p.name).replace('{email}', email).replace('{senha}', pw).replace('{id_compra}', pur.purchase_id).replace('{data}', pur.purchase_date.strftime('%d/%m/%Y')).replace('{vencimento}', pur.expiration_date.strftime('%d/%m/%Y'))
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='back')]]), parse_mode='Markdown')
    
    # ============ COMPRAR MÚLTIPLO ============
    elif d.startswith('multi_'):
        pid = int(d.replace('multi_', ''))
        p = db.get_product(pid)
        waiting[u.id] = f'multi_{pid}'
        txt = db.get_setting('multi_text', '')
        txt = txt.replace('{estoque}', str(p.stock)).replace('{nome}', p.name)
        await q.message.reply_text(txt)
    
    # ============ PIX DA COMPRA ============
    elif d.startswith('pixbuy_'):
        amt = float(d.replace('pixbuy_', ''))
        await q.edit_message_text('⏳ Gerando pagamento...')
        await gen_pix(q.message, u, amt, bal)
    
    # ============ MEU PAINEL (m2) ============
    elif d == 'm2':
        txt = db.get_setting('profile_text', '')
        txt = txt.replace('{id}', str(u.id)).replace('{saldo}', f'R$ {bal:.2f}').replace('{whatsapp}', du.whatsapp or 'Não cadastrado').replace('{compras}', str(du.total_purchases)).replace('{gasto}', f'R$ {du.total_spent:.2f}').replace('{recarregado}', f'R$ {du.total_recharged:.2f}').replace('{gifts}', f'R$ {du.gifts_redeemed:.2f}').replace('{indicacoes}', str(du.total_referrals)).replace('{pontos}', str(du.affiliate_points)).replace('{link}', f't.me/bot?start={u.id}').replace('{codigo}', du.referral_code or '')
        kb = [
            [InlineKeyboardButton(db.get_setting('history_btn', '📋 Histórico'), callback_data='history')],
            [InlineKeyboardButton(db.get_setting('convert_btn', '💱 Trocar Pontos'), callback_data='convert')],
            [InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='back')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    
    # ============ HISTÓRICO ============
    elif d == 'history':
        purs = db.get_user_purchases(u.id)
        user_data = {'id': str(u.id), 'nome': u.first_name or '', 'username': u.username or '', 'saldo': bal, 'db_id': du.id if du else 0}
        pdf = PDFService.generate_history(user_data, purs)
        await q.message.reply_document(document=pdf, filename=f'historico_{u.id}.pdf', caption="📄 Histórico detalhado")
        
        txt = db.get_setting('history_text', 'Histórico:\n\n')
        if purs:
            for p in purs[:5]:
                txt += f"🛍 {p.product_name}\n⏰ {p.purchase_date.strftime('%d/%m/%Y')}\n💰 R$ {p.amount:.2f}\n🎫 {p.purchase_id}\n\n"
            if len(purs) > 5: txt += f"...e mais {len(purs)-5} compras. Veja o PDF!"
        else: txt += "Nenhuma compra."
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='m2')]]), parse_mode='Markdown')
    
    # ============ CONVERSÃO ============
    elif d == 'convert':
        pts = du.affiliate_points if du else 0
        mult = float(db.get_setting('affiliate_multiplier', '0.01'))
        val = pts * mult
        waiting[u.id] = 'convert_points'
        sec = db.get_setting('convert_seconds', '80')
        txt = db.get_setting('convert_text', '')
        txt = txt.replace('{pontos}', str(pts)).replace('{valor}', f'R$ {val:.2f}').replace('{segundos}', sec)
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='m2')]]))
    
    # ============ ADICIONAR CRÉDITOS (m3) ============
    elif d == 'm3':
        txt = db.get_setting('recarga_text', '')
        txt = txt.replace('{saldo}', f'R$ {bal:.2f}').replace('{id}', str(u.id))
        kb = [
            [InlineKeyboardButton(db.get_setting('pix_auto_btn', '💠 Pix Rápido'), callback_data='recarga_pix')],
            [InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='back')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    
    # ============ PIX RECARGA ============
    elif d == 'recarga_pix':
        mn = db.get_setting('deposit_min', '2')
        mx = db.get_setting('deposit_max', '150')
        bon = db.get_setting('bonus_percentage', '0')
        bm = db.get_setting('bonus_min_value', '10')
        txt = db.get_setting('pix_ask_text', '')
        txt = txt.replace('{min}', mn).replace('{max}', mx).replace('{bonus}', bon).replace('{bonus_min}', bm)
        waiting[u.id] = 'recharge_value'
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('cancel_btn', '❌ Cancelar'), callback_data='m3')]]))
    
    # ============ AFILIADO (m4) ============
    elif d == 'm4':
        txt = db.get_setting('affiliate_text', '')
        txt = txt.replace('{link}', f't.me/bot?start={u.id}').replace('{codigo}', du.referral_code or '')
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='back')]]), parse_mode='Markdown')
    
    # ============ RANKINGS (m5) ============
    elif d == 'm5':
        txt = db.get_setting('ranking_text', '📊 Selecione o ranking:')
        kb = [
            [InlineKeyboardButton(db.get_setting('rank_balance_btn', '🏆 Top Saldo'), callback_data='rank_balance')],
            [InlineKeyboardButton(db.get_setting('rank_recharge_btn', '💠 Top Depósitos'), callback_data='rank_recharge')],
            [InlineKeyboardButton(db.get_setting('rank_products_btn', '📦 Top Produtos'), callback_data='rank_products')],
            [InlineKeyboardButton(db.get_setting('rank_recent_btn', '📈 Top Recentes'), callback_data='rank_recent')],
            [InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='back')]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    
    elif d.startswith('rank_'):
        tp = d.replace('rank_', '')
        txt = ''
        if tp == 'balance':
            us = db.get_top_balance(20)
            txt = "🏆 Top 20 Saldo:\n\n"
            for i, uu in enumerate(us, 1): txt += f"{i}º {uu.first_name or f'ID:{uu.telegram_id}'} - R$ {uu.balance:.2f}\n"
        elif tp == 'recharge':
            us = db.get_top_rechargers(10)
            txt = "💠 Top 10 Depósitos:\n\n"
            for i, uu in enumerate(us, 1): txt += f"{i}º {uu.first_name or f'ID:{uu.telegram_id}'} - R$ {uu.total_recharged:.2f}\n"
        elif tp == 'products':
            ps = db.get_top_products(10)
            txt = "📦 Top 10 Produtos:\n\n"
            for i, pp in enumerate(ps, 1): txt += f"{i}º {pp.name} - {pp.total_sold} vendas\n"
        elif tp == 'recent':
            us = db.get_recent_rechargers(10)
            txt = "📈 Top 10 Recentes:\n\n"
            for i, (uu, tt) in enumerate(us, 1): txt += f"{i}º {uu.first_name or f'ID:{uu.telegram_id}'} - R$ {tt:.2f}\n"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='m5')]]))
    
    # ============ ESTOQUE (m6) ============
    elif d == 'm6':
        stock = db.get_stock_list()
        txt = db.get_setting('stock_text', '📦 Estoque:\n\n')
        if stock:
            for n, q in stock.items(): txt += f"📦 {n}: {q} unid.\n"
        else:
            txt += "Nenhum item em estoque."
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='back')]]))
    
    # ============ SUPORTE (m7) ============
    elif d == 'm7':
        link = db.get_setting('support_link', '')
        txt = db.get_setting('support_text', '📞 Suporte')
        if link:
            await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='back'), InlineKeyboardButton('📞 Falar', url=link)]]))
        else:
            await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='back')]]))
    
    # ============ TERMOS (m8) ============
    elif d == 'm8':
        txt = db.get_setting('terms_text', 'Termos de uso.')
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text', '🔙 Voltar'), callback_data='back')]]), parse_mode='Markdown')
    
    # ============ VOLTAR ============
    elif d == 'back':
        await start(update, context)

async def gen_pix(msg, u, amt, bal):
    ps = PixService()
    r = ps.gerar_pix(u.id, amt)
    if r['sucesso']:
        bp = float(db.get_setting('bonus_percentage', '0'))
        bm = float(db.get_setting('bonus_min_value', '10'))
        bonus = amt * (bp/100) if amt >= bm and bp > 0 else 0
        txt = db.get_setting('pix_result_text', '')
        txt = txt.replace('{valor}', f'R$ {amt:.2f}').replace('{id}', r['pix_id']).replace('{copia_cola}', r['copia_cola']).replace('{saldo}', f'R$ {bal:.2f}').replace('{bonus}', f'R$ {bonus:.2f}').replace('{total}', f'R$ {bal+amt+bonus:.2f}').replace('{expiracao}', str(r['expiracao_minutos']))
        kb = [
            [InlineKeyboardButton(db.get_setting('wait_btn', '🔄 Aguardando'), callback_data='none')],
            [InlineKeyboardButton(db.get_setting('copy_btn', '📋 Copiar PIX'), callback_data='none')]
        ]
        if r.get('qr_code_imagem'):
            await msg.reply_photo(photo=r['qr_code_imagem'], caption=txt, reply_markup=InlineKeyboardMarkup(kb))
        else:
            await msg.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    ps.close()

async def handle_msg(update, context):
    u = update.effective_user
    txt = update.message.text
    if txt.startswith('/'): return
    if db.check_flood(u.id):
        ftxt = db.get_setting('flood_text', '⚠️ Aguarde {segundos}s.').replace('{segundos}', db.get_setting('flood_seconds', '6'))
        await update.message.reply_text(ftxt)
        return
    await start(update, context)
