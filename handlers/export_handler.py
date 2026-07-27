from database.db_manager import DBManager
from services.pdf_service import PDFService
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import csv

db = DBManager()

async def export_users_csv(update, context):
    from database.models import SessionLocal, User
    session = SessionLocal()
    users = session.query(User).all()
    
    output = BytesIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Telegram ID', 'Nome', 'Username', 'Saldo', 'Compras', 'Gasto Total'])
    
    for u in users:
        writer.writerow([u.id, u.telegram_id, u.first_name, u.username, u.balance, u.total_purchases, u.total_spent])
    
    output.seek(0)
    await update.message.reply_document(document=output, filename='usuarios.csv')
    session.close()

async def export_sales_csv(update, context):
    from database.models import SessionLocal, Purchase
    session = SessionLocal()
    sales = session.query(Purchase).all()
    
    output = BytesIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Usuário', 'Produto', 'Valor', 'Data', 'Status'])
    
    for s in sales:
        writer.writerow([s.id, s.user_id, s.product_name, s.amount, s.purchase_date.strftime('%d/%m/%Y'), s.status])
    
    output.seek(0)
    await update.message.reply_document(document=output, filename='vendas.csv')
    session.close()

async def export_full_report(update, context):
    user = update.effective_user
    db_user = db.get_user(user.id)
    purchases = db.get_user_purchases(user.id)
    
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, "Relatório Completo")
    c.setFont("Helvetica", 10)
    c.drawString(50, 780, f"ID: {user.id}")
    c.drawString(50, 765, f"Nome: {user.first_name or ''}")
    c.drawString(50, 750, f"Saldo: R$ {db_user.balance:.2f}" if db_user else "")
    
    y = 720
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Compras:")
    c.setFont("Helvetica", 9)
    y -= 20
    
    for p in purchases:
        if y < 100:
            c.showPage()
            y = 800
        c.drawString(50, y, f"Produto: {p.product_name} | Valor: R$ {p.amount:.2f} | Data: {p.purchase_date.strftime('%d/%m/%Y')}")
        y -= 12
        if p.email:
            c.drawString(50, y, f"Email: {p.email} | Senha: {p.password}")
            y -= 12
        y -= 8
    
    c.save()
    buf.seek(0)
    await update.message.reply_document(document=buf, filename='relatorio.pdf')
