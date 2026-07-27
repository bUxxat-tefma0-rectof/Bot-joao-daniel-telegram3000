from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager
from database.models import SessionLocal, Tenant, User
from config.settings import BOT_TOKEN, ADMIN_ID
import uuid

db = DBManager()

async def show_rental_menu(update, context):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    
    if user.id != ADMIN_ID:
        await q.edit_message_text("❌ Acesso restrito!")
        return
    
    session = SessionLocal()
    tenants = session.query(Tenant).all()
    session.close()
    
    txt = "🏢 *Aluguel de Bots*\n\n"
    for t in tenants:
        txt += f"🆔 {t.id} - {t.name}\n"
        txt += f"📊 Status: {t.status}\n"
        txt += f"📅 Plano: {t.plan}\n\n"
    
    kb = [
        [InlineKeyboardButton("➕ Novo Cliente", callback_data='rental_create')],
        [InlineKeyboardButton("📋 Listar Clientes", callback_data='rental_list')],
        [InlineKeyboardButton("🔧 Gerenciar Cliente", callback_data='rental_manage')],
        [InlineKeyboardButton("🔙 Voltar", callback_data='admin')]
    ]
    
    await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def create_tenant(update, context):
    q = update.callback_query
    await q.answer()
    
    tenant_name = f"Store_{uuid.uuid4().hex[:6]}"
    bot_token = f"BOT_TOKEN_{uuid.uuid4().hex[:8]}"
    
    session = SessionLocal()
    tenant = Tenant(
        name=tenant_name,
        bot_token=bot_token,
        owner_id=q.from_user.id,
        status='active',
        plan='basic',
        expiration_date=__import__('datetime').datetime.now() + __import__('datetime').timedelta(days=30)
    )
    session.add(tenant)
    session.commit()
    session.close()
    
    from database.models import Setting
    session = SessionLocal()
    defaults = {
        'welcome_text': '', 'support_link': '', 'pix_expiration': '15',
        'deposit_min': '2', 'deposit_max': '150', 'bonus_percentage': '0',
        'commission_percentage': '10', 'btn1_text': '🛍️ Comprar',
        'btn2_text': '👤 Perfil', 'btn3_text': '💰 Recarregar',
        'btn4_text': '💼 Afiliado', 'btn1_pos': 'full',
        'btn2_pos': 'left', 'btn3_pos': 'right', 'btn4_pos': 'full',
    }
    for k, v in defaults.items():
        session.add(Setting(tenant_id=tenant.id, key=k, value=v))
    session.commit()
    session.close()
    
    await q.edit_message_text(f"✅ Cliente criado!\n\nNome: {tenant_name}\nToken: {bot_token}")

async def list_tenants(update, context):
    session = SessionLocal()
    tenants = session.query(Tenant).all()
    session.close()
    
    txt = "📋 *Clientes*\n\n"
    for t in tenants:
        txt += f"🆔 {t.id} - {t.name}\n📊 {t.status} | {t.plan}\n\n"
    
    await update.callback_query.edit_message_text(txt, parse_mode='Markdown')

async def manage_tenant(update, context):
    q = update.callback_query
    await q.answer()
    
    kb = [
        [InlineKeyboardButton("✏️ Editar Nome", callback_data='rental_edit_name')],
        [InlineKeyboardButton("🔄 Mudar Plano", callback_data='rental_edit_plan')],
        [InlineKeyboardButton("⏰ Renovar", callback_data='rental_renew')],
        [InlineKeyboardButton("🚫 Suspender", callback_data='rental_suspend')],
        [InlineKeyboardButton("✅ Ativar", callback_data='rental_activate')],
        [InlineKeyboardButton("🔙 Voltar", callback_data='admin')]
    ]
    
    await q.edit_message_text("🔧 Gerenciar Cliente\n\nSelecione uma ação:", reply_markup=InlineKeyboardMarkup(kb))
