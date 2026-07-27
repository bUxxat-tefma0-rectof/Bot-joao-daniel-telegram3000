from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import DBManager
from database.models import SessionLocal, Tenant
from config.settings import ADMIN_ID
import uuid

db = DBManager()

async def show_rental_menu(update, context):
    q = update.callback_query
    await q.answer()
    if q.from_user.id != ADMIN_ID: await q.edit_message_text("❌ Acesso restrito!"); return
    
    session = SessionLocal()
    tenants = session.query(Tenant).all()
    session.close()
    
    txt = "🏢 Aluguel de Bots\n\n"
    for t in tenants: txt += f"🆔 {t.id} - {t.name} | {t.status} | {t.plan}\n"
    
    kb = [
        [InlineKeyboardButton("➕ Novo Cliente", callback_data='rental_create')],
        [InlineKeyboardButton("📋 Listar", callback_data='rental_list')],
        [InlineKeyboardButton("🔙 Voltar", callback_data='adm_back')]
    ]
    await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def create_tenant(update, context):
    q = update.callback_query
    await q.answer()
    name = f"Store_{uuid.uuid4().hex[:6]}"
    session = SessionLocal()
    tenant = Tenant(name=name, bot_token=f"BOT_{uuid.uuid4().hex}", owner_id=q.from_user.id, status='active', plan='basic')
    session.add(tenant)
    session.commit()
    session.close()
    await q.edit_message_text(f"✅ Cliente criado: {name}")

async def list_tenants(update, context):
    session = SessionLocal()
    tenants = session.query(Tenant).all()
    session.close()
    txt = "📋 Clientes\n\n"
    for t in tenants: txt += f"🆔 {t.id} - {t.name}\n"
    await update.callback_query.edit_message_text(txt)

async def manage_tenant(update, context):
    await update.callback_query.edit_message_text("🔧 Gerenciar Cliente\n\nEm breve!")
