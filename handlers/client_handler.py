from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager
from services.pix_service import PixService
from services.login_service import LoginService
from services.affiliate_service import AffiliateService
from services.pdf_service import PDFService

db=DBManager()
waiting={}
selected={}

def build_kb():
    p=[db.get_setting(f'btn{i}_pos','full') for i in range(1,9)]
    b=[db.get_setting(f'btn{i}_text','') for i in range(1,9)]
    kb=[]
    if b[0]: kb.append([InlineKeyboardButton(b[0],callback_data='m1')])
    r2=[]
    if p[1] in ['left','full'] and b[1]: r2.append(InlineKeyboardButton(b[1],callback_data='m2'))
    if p[2] in ['right','full'] and b[2]: r2.append(InlineKeyboardButton(b[2],callback_data='m3'))
    if r2: kb.append(r2)
    r3=[]
    if p[3] in ['left','full'] and b[3]: r3.append(InlineKeyboardButton(b[3],callback_data='m4'))
    if p[4] in ['right','full'] and b[4]: r3.append(InlineKeyboardButton(b[4],callback_data='m5'))
    if r3: kb.append(r3)
    if b[5]: kb.append([InlineKeyboardButton(b[5],callback_data='m6')])
    if b[6]: kb.append([InlineKeyboardButton(b[6],callback_data='m7')])
    if b[7]: kb.append([InlineKeyboardButton(b[7],callback_data='m8')])
    return kb

async def start(update, context):
    u=update.effective_user
    du=db.get_user(u.id) or db.create_user(u.id,u.username,u.first_name)
    w=db.get_setting('welcome_text','')
    w=w.replace('{id}',str(u.id)).replace('{saldo}',f'R$ {du.balance:.2f}').replace('{nome}',u.first_name or '').replace('{username}',f'@{u.username}' if u.username else '').replace('{indicacoes}',str(du.total_referrals))
    img=db.get_setting('welcome_image','')
    kb=build_kb(); reply=InlineKeyboardMarkup(kb)
    if img:
        try: await update.message.reply_photo(photo=img,caption=w,reply_markup=reply)
        except: await update.message.reply_text(w,reply_markup=reply)
    else: await update.message.reply_text(w,reply_markup=reply)

async def callback(update, context):
    q=update.callback_query; await q.answer(); d=q.data; u=q.from_user
    du=db.get_user(u.id); bal=du.balance if du else 0
    
    if d=='m1':
        prods=db.get_products(); cats=list(set(p.category for p in prods if p.category))
        txt=db.get_setting('catalog_text','').replace('{saldo}',f'R$ {bal:.2f}')
        kb=[]
        if cats: kb=[[InlineKeyboardButton(c,callback_data=f'cat_{c}')] for c in cats]
        else: kb=[[InlineKeyboardButton(p.name,callback_data=f'prod_{p.id}')] for p in prods]
        kb.append([InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='back')])
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup(kb))
    
    elif d.startswith('cat_'):
        cat=d.replace('cat_',''); prods=db.get_products(cat)
        txt=db.get_setting('catalog_text','').replace('{saldo}',f'R$ {bal:.2f}')
        kb=[[InlineKeyboardButton(p.name,callback_data=f'prod_{p.id}')] for p in prods]
        kb.append([InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='m1')])
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup(kb))
    
    elif d.startswith('prod_'):
        pid=int(d.replace('prod_','')); p=db.get_product(pid)
        if not p: return
        txt=db.get_setting('product_text','').replace('{nome}',p.name).replace('{preco}',f'R$ {p.price:.2f}').replace('{saldo}',f'R$ {bal:.2f}').replace('{estoque}',str(p.stock)).replace('{descricao}',p.description or '').replace('{vendidos}',str(p.total_sold)).replace('{garantia}',p.warranty or '')
        selected[u.id]=pid
        kb=[]
        if p.stock>0:
            kb.append([InlineKeyboardButton(db.get_setting('buy_btn','Comprar'),callback_data=f'buy_{pid}')])
            kb.append([InlineKeyboardButton(db.get_setting('multi_btn','Comprar Qtd'),callback_data=f'multi_{pid}')])
        kb.append([InlineKeyboardButton(db.get_setting('add_saldo_btn','Add Saldo'),callback_data='m3')])
        kb.append([InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data=f'cat_{p.category}')])
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup(kb),parse_mode='Markdown')
    
    elif d.startswith('buy_'):
        pid=int(d.replace('buy_','')); p=db.get_product(pid)
        if not p: return
        if bal<p.price:
            falta=p.price-bal
            txt=db.get_setting('insufficient_text','').replace('{saldo}',f'R$ {bal:.2f}').replace('{preco}',f'R$ {p.price:.2f}').replace('{falta}',f'R$ {falta:.2f}')
            kb=[
                [InlineKeyboardButton(db.get_setting('pix_btn','Gerar PIX').replace('{valor}',f'R$ {p.price:.2f}'),callback_data=f'pixbuy_{p.price}')],
                [InlineKeyboardButton(db.get_setting('cancel_btn','Cancelar'),callback_data=f'prod_{pid}')]
            ]
            await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup(kb),parse_mode='Markdown'); return
        if p.stock<=0: await q.edit_message_text("Esgotado"); return
        db.subtract_balance(u.id,p.price); db.decrease_stock(pid)
        ls=LoginService(); login=ls.get(p.name)
        email=login.email if login else ''; pw=login.password if login else ''
        if login: ls.sold(login.id,u.id)
        pur=db.create_purchase(u.id,p.name,p.price,email,pw,''); ls.close()
        af=AffiliateService(); af.add_commission(u.id,p.price); af.close()
        txt=db.get_setting('success_text','Compra realizada!').replace('{nome}',p.name).replace('{email}',email).replace('{senha}',pw).replace('{id_compra}',pur.purchase_id).replace('{data}',pur.purchase_date.strftime('%d/%m/%Y')).replace('{vencimento}',pur.expiration_date.strftime('%d/%m/%Y'))
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='back')]]),parse_mode='Markdown')
    
    elif d.startswith('multi_'):
        pid=int(d.replace('multi_','')); p=db.get_product(pid)
        waiting[u.id]=f'multi_{pid}'
        txt=db.get_setting('multi_text','').replace('{estoque}',str(p.stock)).replace('{nome}',p.name)
        await q.message.reply_text(txt)
    
    elif d.startswith('pixbuy_'):
        amt=float(d.replace('pixbuy_',''))
        await q.edit_message_text('⏳ Gerando pagamento...')
        await gen_pix(q.message,u,amt,bal)
    
    elif d=='m2':
        txt=db.get_setting('profile_text','').replace('{id}',str(u.id)).replace('{saldo}',f'R$ {bal:.2f}').replace('{whatsapp}',du.whatsapp or '').replace('{compras}',str(du.total_purchases)).replace('{gasto}',f'R$ {du.total_spent:.2f}').replace('{recarregado}',f'R$ {du.total_recharged:.2f}').replace('{gifts}',f'R$ {du.gifts_redeemed:.2f}').replace('{indicacoes}',str(du.total_referrals)).replace('{pontos}',str(du.affiliate_points)).replace('{link}',f't.me/bot?start={u.id}').replace('{codigo}',du.referral_code or '')
        kb=[
            [InlineKeyboardButton(db.get_setting('history_btn','Histórico'),callback_data='history')],
            [InlineKeyboardButton(db.get_setting('convert_btn','Trocar Pontos'),callback_data='convert')],
            [InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='back')]
        ]
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup(kb),parse_mode='Markdown')
    
    elif d=='history':
        purs=db.get_user_purchases(u.id)
        txt=db.get_setting('history_text','Histórico:\n\n')
        for p in purs[:20]:
            txt+=f"🛍 {p.product_name}\n⏰ {p.purchase_date.strftime('%d/%m/%Y')}\n📆 {p.expiration_date.strftime('%d/%m/%Y') if p.expiration_date else 'N/A'}\n💰 R$ {p.amount:.2f}\n🎫 {p.purchase_id}\n"
            if p.email: txt+=f"📧 {p.email}\n🔐 {p.password}\n"
            if p.activation_link: txt+=f"🔗 {p.activation_link}\n"
            txt+="\n"
        pdf=PDFService.generate_history({'id':str(u.id),'nome':u.first_name or '','saldo':bal},purs)
        await q.message.reply_document(document=pdf,filename='historico.pdf')
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='m2')]]),parse_mode='Markdown')
    
    elif d=='convert':
        pts=du.affiliate_points if du else 0; mult=float(db.get_setting('affiliate_multiplier','0.01')); val=pts*mult
        waiting[u.id]='convert_points'; sec=db.get_setting('convert_seconds','80')
        txt=db.get_setting('convert_text','').replace('{pontos}',str(pts)).replace('{valor}',f'R$ {val:.2f}').replace('{segundos}',sec)
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='m2')]]))
    
    elif d=='m3':
        txt=db.get_setting('recarga_text','').replace('{saldo}',f'R$ {bal:.2f}').replace('{id}',str(u.id))
        kb=[
            [InlineKeyboardButton(db.get_setting('pix_auto_btn','Pix Automático'),callback_data='recarga_pix')],
            [InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='back')]
        ]
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup(kb))
    
    elif d=='recarga_pix':
        mn=db.get_setting('deposit_min','2'); mx=db.get_setting('deposit_max','150')
        bon=db.get_setting('bonus_percentage','0'); bm=db.get_setting('bonus_min_value','10')
        txt=db.get_setting('pix_ask_text','').replace('{min}',mn).replace('{max}',mx).replace('{bonus}',bon).replace('{bonus_min}',bm)
        waiting[u.id]='recharge_value'
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('cancel_btn','Cancelar'),callback_data='m3')]]))
    
    elif d=='m4':
        txt=db.get_setting('affiliate_text','').replace('{link}',f't.me/bot?start={u.id}').replace('{codigo}',du.referral_code or '')
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='back')]]),parse_mode='Markdown')
    
    elif d=='m5':
        txt=db.get_setting('ranking_text','')
        kb=[
            [InlineKeyboardButton(db.get_setting('rank_balance_btn','Saldo'),callback_data='rank_balance')],
            [InlineKeyboardButton(db.get_setting('rank_recharge_btn','Depósitos'),callback_data='rank_recharge')],
            [InlineKeyboardButton(db.get_setting('rank_products_btn','Produtos'),callback_data='rank_products')],
            [InlineKeyboardButton(db.get_setting('rank_recent_btn','Recentes'),callback_data='rank_recent')],
            [InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='back')]
        ]
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup(kb))
    
    elif d.startswith('rank_'):
        tp=d.replace('rank_',''); txt=''
        if tp=='balance':
            us=db.get_top_balance(20); txt="Top 20 Saldo:\n\n"
            for i,uu in enumerate(us,1): txt+=f"{i}º {uu.first_name or f'ID:{uu.telegram_id}'} - R$ {uu.balance:.2f}\n"
        elif tp=='recharge':
            us=db.get_top_rechargers(10); txt="Top 10 Depósitos:\n\n"
            for i,uu in enumerate(us,1): txt+=f"{i}º {uu.first_name or f'ID:{uu.telegram_id}'} - R$ {uu.total_recharged:.2f}\n"
        elif tp=='products':
            ps=db.get_top_products(10); txt="Top 10 Produtos:\n\n"
            for i,pp in enumerate(ps,1): txt+=f"{i}º {pp.name} - {pp.total_sold} vendas\n"
        elif tp=='recent':
            us=db.get_recent_rechargers(10); txt="Top 10 Recentes:\n\n"
            for i,(uu,tt) in enumerate(us,1): txt+=f"{i}º {uu.first_name or f'ID:{uu.telegram_id}'} - R$ {tt:.2f}\n"
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='m5')]]))
    
    elif d=='m6':
        stock=db.get_stock_list(); txt=db.get_setting('stock_text','')
        for n,q in stock.items(): txt+=f"{n}: {q}\n"
        await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='back')]]))
    
    elif d=='m7':
        link=db.get_setting('support_link',''); txt=db.get_setting('support_text','')
        if link: await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='back'),InlineKeyboardButton('Abrir',url=link)]]))
        else: await q.edit_message_text(txt,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='back')]]))
    
    elif d=='m8': await q.edit_message_text(db.get_setting('terms_text',''),reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(db.get_setting('back_text','Voltar'),callback_data='back')]]),parse_mode='Markdown')
    
    elif d=='back': await start(update,context)

async def gen_pix(msg,u,amt,bal):
    ps=PixService(); r=ps.gerar_pix(u.id,amt)
    if r['sucesso']:
        bp=float(db.get_setting('bonus_percentage','0')); bm=float(db.get_setting('bonus_min_value','10'))
        bonus=amt*(bp/100) if amt>=bm and bp>0 else 0
        txt=db.get_setting('pix_result_text','').replace('{valor}',f'R$ {amt:.2f}').replace('{id}',r['pix_id']).replace('{copia_cola}',r['copia_cola']).replace('{saldo}',f'R$ {bal:.2f}').replace('{bonus}',f'R$ {bonus:.2f}').replace('{total}',f'R$ {bal+amt+bonus:.2f}').replace('{expiracao}',str(r['expiracao_minutos']))
        kb=[[InlineKeyboardButton(db.get_setting('wait_btn','Aguardando'),callback_data='none')],[InlineKeyboardButton(db.get_setting('copy_btn','Copiar PIX'),callback_data='none')]]
        if r.get('qr_code_imagem'): await msg.reply_photo(photo=r['qr_code_imagem'],caption=txt,reply_markup=InlineKeyboardMarkup(kb))
        else: await msg.reply_text(txt,reply_markup=InlineKeyboardMarkup(kb))
    ps.close()

async def handle_msg(update,context):
    u=update.effective_user; txt=update.message.text
    if txt.startswith('/'): return
    if u.id==int(__import__('config.settings').ADMIN_ID) and u.id in waiting:
        state=waiting[u.id]
        fm={'welcome':'welcome_text','image':'welcome_image','support':'support_link','recarga_text':'recarga_text','pix_ask_text':'pix_ask_text','pix_result_text':'pix_result_text','catalog_text':'catalog_text','product_text':'product_text','insufficient_text':'insufficient_text','expired_pix_text':'expired_pix_text','profile_text':'profile_text','stock_text':'stock_text','ranking_text':'ranking_text','multi_text':'multi_text','convert_text':'convert_text','success_text':'success_text','history_text':'history_text','terms_text':'terms_text','support_text':'support_text','flood_text':'flood_text','gift_text':'gift_text','faq_text':'faq_text','buy_btn':'buy_btn','multi_btn':'multi_btn','add_saldo_btn':'add_saldo_btn','pix_btn':'pix_btn','cancel_btn':'cancel_btn','back_text':'back_text','history_btn':'history_btn','convert_btn':'convert_btn','wait_btn':'wait_btn','copy_btn':'copy_btn','pix_auto_btn':'pix_auto_btn','rank_balance_btn':'rank_balance_btn','rank_recharge_btn':'rank_recharge_btn','rank_products_btn':'rank_products_btn','rank_recent_btn':'rank_recent_btn','mp_token':'mp_access_token','deposit_min':'deposit_min','deposit_max':'deposit_max','expiration':'pix_expiration','bonus':'bonus_percentage','bonus_min':'bonus_min_value','commission':'commission_percentage','flood_seconds':'flood_seconds','convert_seconds':'convert_seconds','btn1':'btn1_text','btn2':'btn2_text','btn3':'btn3_text','btn4':'btn4_text','btn5':'btn5_text','btn6':'btn6_text','btn7':'btn7_text','btn8':'btn8_text'}
        if state=='pos':
            for i,p in enumerate(txt.split('|')[:8],1):
                if p.strip() in ['full','left','right']: db.set_setting(f'btn{i}_pos',p.strip())
            await update.message.reply_text("✅")
        elif state=='broadcast':
            from database.models import SessionLocal, User as U
            s=SessionLocal(); users=s.query(U).all(); c=0
            for uu in users:
                try: await context.bot.send_message(uu.telegram_id,txt); c+=1
                except: pass
            s.close(); await update.message.reply_text(f"✅ {c}")
        elif state=='recharge_value':
            try:
                amt=float(txt); mn=float(db.get_setting('deposit_min','2')); mx=float(db.get_setting('deposit_max','150'))
                if amt<mn: await update.message.reply_text(f"❌ Mín R$ {mn:.2f}")
                elif amt>mx: await update.message.reply_text(f"❌ Máx R$ {mx:.2f}")
                else: await update.message.reply_text("⏳ Gerando..."); await gen_pix(update.message,u,amt,db.get_balance(u.id))
            except: await update.message.reply_text("❌ Inválido")
        elif state.startswith('multi_'):
            try:
                qty=int(txt); pid=int(state.replace('multi_','')); p=db.get_product(pid); bal=db.get_balance(u.id); total=p.price*qty
                if qty>p.stock: await update.message.reply_text(f"❌ Estoque: {p.stock}")
                elif bal<total:
                    falta=total-bal
                    kb=[[InlineKeyboardButton(f"Gerar PIX R$ {total:.2f}",callback_data=f'pixbuy_{total}')]]
                    await update.message.reply_text(f"❌ Falta R$ {falta:.2f}",reply_markup=InlineKeyboardMarkup(kb))
                else:
                    for _ in range(qty): db.subtract_balance(u.id,p.price); db.decrease_stock(pid)
                    await update.message.reply_text(f"✅ {qty}x {p.name}")
            except: await update.message.reply_text("❌ Inválido")
        elif state=='convert_points':
            try:
                pts=int(txt); mult=float(db.get_setting('affiliate_multiplier','0.01')); du=db.get_user(u.id)
                if pts<=du.affiliate_points: val=pts*mult; du.affiliate_points-=pts; du.balance+=val; db.db.commit(); await update.message.reply_text(f"✅ R$ {val:.2f}")
                else: await update.message.reply_text("❌ Pontos insuficientes")
            except: await update.message.reply_text("❌ Inválido")
        elif state in fm: db.set_setting(fm[state],txt); await update.message.reply_text("✅ Salvo!")
        else: await update.message.reply_text("✅ OK")
        del waiting[u.id]; return
    if db.check_flood(u.id):
        txt=db.get_setting('flood_text','⚠️ Pare de floodar! Aguarde {segundos}s.').replace('{segundos}',db.get_setting('flood_seconds','6'))
        await update.message.reply_text(txt); return
    await start(update,context)
