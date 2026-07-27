from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from datetime import datetime
from database.db_manager import DBManager

db = DBManager()

class PDFService:
    @staticmethod
    def generate_history(user_data, purchases):
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        
        bot_name = db.get_setting('bot_name', 'STORE BOT')
        username = user_data.get('username', '')
        
        # Título
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 800, f"HISTÓRICO DETALHADO @{bot_name}")
        
        # Linha separadora
        c.line(50, 790, 550, 790)
        
        # Dados do usuário
        c.setFont("Helvetica", 10)
        c.drawString(50, 770, f"ID: {user_data.get('id', '')}")
        c.drawString(50, 755, f"Nome: {user_data.get('nome', '')}")
        if username:
            c.drawString(50, 740, f"Username: @{username}")
        c.drawString(50, 725, f"Saldo: R$ {user_data.get('saldo', 0):.2f}")
        
        # Seção COMPRAS
        y = 690
        c.line(50, y+5, 550, y+5)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "COMPRAS:")
        y -= 5
        c.line(50, y, 550, y)
        c.setFont("Helvetica", 9)
        y -= 20
        
        if not purchases:
            c.drawString(50, y, "Nenhuma compra realizada.")
        else:
            for i, p in enumerate(purchases, 1):
                if y < 100:
                    c.showPage()
                    y = 800
                
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, f"🛍 Compras: {i}")
                c.setFont("Helvetica", 9)
                y -= 15
                
                c.drawString(60, y, f"⏰ Data da compra: {p.purchase_date.strftime('%d/%m/%Y')}")
                y -= 12
                
                if p.expiration_date:
                    c.drawString(60, y, f"📆 Vencimento: {p.expiration_date.strftime('%d/%m/%Y')}")
                    y -= 12
                
                c.drawString(60, y, f"💰 Valor: R$ {p.amount:.2f}")
                y -= 12
                
                c.drawString(60, y, f"🎫 ID da compra: {p.purchase_id}")
                y -= 12
                
                c.drawString(60, y, f"⚜️ Serviço: {p.product_name}")
                y -= 12
                
                if p.email:
                    c.drawString(60, y, f"📧 Email: {p.email}")
                    y -= 12
                
                if p.password:
                    c.drawString(60, y, f"🔐 Senha: {p.password}")
                    y -= 12
                
                if p.activation_link:
                    c.drawString(60, y, f"📃 Nota: {p.activation_link}")
                    y -= 12
                
                y -= 15
        
        # Seção PAGAMENTOS
        y -= 10
        c.line(50, y+5, 550, y+5)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "PAGAMENTOS:")
        y -= 5
        c.line(50, y, 550, y)
        c.setFont("Helvetica", 9)
        y -= 20
        
        from database.models import SessionLocal, PixRecharge
        session = SessionLocal()
        recharges = session.query(PixRecharge).filter_by(
            user_id=user_data.get('db_id', 0), 
            status='completed'
        ).order_by(PixRecharge.paid_at.desc()).all()
        
        if not recharges:
            c.drawString(50, y, "Nenhum pagamento realizado.")
        else:
            for r in recharges[:20]:
                if y < 100:
                    c.showPage()
                    y = 800
                
                c.drawString(60, y, f"💠 PIX - R$ {r.amount:.2f}")
                y -= 12
                if r.paid_at:
                    c.drawString(60, y, f"📅 Pago em: {r.paid_at.strftime('%d/%m/%Y %H:%M')}")
                    y -= 12
                if r.bonus_amount > 0:
                    c.drawString(60, y, f"🎁 Bônus: R$ {r.bonus_amount:.2f}")
                    y -= 12
                c.drawString(60, y, f"🆔 ID: {r.pix_id}")
                y -= 20
        
        session.close()
        
        # Rodapé
        c.line(50, 50, 550, 50)
        c.setFont("Helvetica", 8)
        c.drawString(50, 35, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        c.drawString(50, 22, f"@{bot_name} - Todos os direitos reservados")
        
        c.save()
        buf.seek(0)
        return buf
    
    @staticmethod
    def generate_purchase_receipt(user_data, purchase):
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        
        bot_name = db.get_setting('bot_name', 'STORE BOT')
        
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 800, f"COMPROVANTE DE COMPRA")
        c.setFont("Helvetica", 10)
        c.drawString(50, 780, f"@{bot_name}")
        
        c.line(50, 770, 550, 770)
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 750, f"🛍 Compras: 1")
        c.setFont("Helvetica", 10)
        
        y = 730
        dados = [
            (f"⏰ Data da compra:", purchase.purchase_date.strftime('%d/%m/%Y')),
            (f"📆 Vencimento:", purchase.expiration_date.strftime('%d/%m/%Y') if purchase.expiration_date else 'N/A'),
            (f"💰 Valor:", f"R$ {purchase.amount:.2f}"),
            (f"🎫 ID da compra:", purchase.purchase_id),
            (f"⚜️ Serviço:", purchase.product_name),
        ]
        
        if purchase.email:
            dados.append((f"📧 Email:", purchase.email))
        if purchase.password:
            dados.append((f"🔐 Senha:", purchase.password))
        if purchase.activation_link:
            dados.append((f"📃 Nota:", purchase.activation_link))
        
        for label, value in dados:
            c.drawString(60, y, f"{label} {value}")
            y -= 18
        
        c.line(50, 100, 550, 100)
        c.setFont("Helvetica", 8)
        c.drawString(50, 85, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        c.drawString(50, 72, f"@{bot_name}")
        
        c.save()
        buf.seek(0)
        return buf
