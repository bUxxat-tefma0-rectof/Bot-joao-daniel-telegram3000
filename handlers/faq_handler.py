from database.db_manager import DBManager
from database.models import SessionLocal, FAQ
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

db = DBManager()

async def show_faq(update, context):
    session = SessionLocal()
    faqs = session.query(FAQ).filter_by(tenant_id=1).order_by(FAQ.position).all()
    
    if not faqs:
        await update.message.reply_text("Nenhuma FAQ cadastrada!")
        session.close()
        return
    
    txt = "📋 *FAQ - Perguntas Frequentes*\n\n"
    kb = []
    
    for faq in faqs[:10]:
        kb.append([InlineKeyboardButton(faq.question[:50], callback_data=f'faq_{faq.id}')])
    
    kb.append([InlineKeyboardButton("🔙 Voltar", callback_data='back')])
    
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    session.close()

async def show_faq_detail(update, context):
    q = update.callback_query
    await q.answer()
    faq_id = int(q.data.replace('faq_', ''))
    
    session = SessionLocal()
    faq = session.query(FAQ).filter_by(id=faq_id).first()
    
    if faq:
        txt = f"❓ *{faq.question}*\n\n💬 {faq.answer}"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Voltar", callback_data='show_faq')]
        ]), parse_mode='Markdown')
    
    session.close()

async def add_faq(update, context):
    args = context.args
    if len(args) >= 2:
        separator = db.get_setting('separator', '===')
        text = ' '.join(args)
        parts = text.split(separator)
        
        if len(parts) >= 2:
            session = SessionLocal()
            faq = FAQ(
                tenant_id=1,
                question=parts[0].strip(),
                answer=parts[1].strip(),
                position=session.query(FAQ).count()
            )
            session.add(faq)
            session.commit()
            session.close()
            await update.message.reply_text("✅ FAQ adicionada!")
        else:
            await update.message.reply_text(f"❌ Use: /addfaq pergunta{separator}resposta")
