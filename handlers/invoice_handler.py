from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from database.db_manager import DBManager

db = DBManager()

class InvoiceHandler:
    @staticmethod
    def generate_invoice(user_id, purchase_data):
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, 800, "COMPROVANTE DE COMPRA")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, 770, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        c.drawString(50, 750, f"Cliente ID: {user_id}")
        
        c.line(50, 730, 550, 730)
        
        y = 710
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "DADOS DO PRODUTO")
        c.setFont("Helvetica", 12)
        y -= 25
        
        c.drawString(50, y, f"Produto: {purchase_data.get('product_name', '')}"); y -= 20
        c.drawString(50, y, f"Valor: R$ {purchase_data.get('amount', 0):.2f}"); y -= 20
        c.drawString(50, y, f"ID da Compra: {purchase_data.get('purchase_id', '')}"); y -= 20
        
        if purchase_data.get('email'):
            c.drawString(50, y, f"Email: {purchase_data.get('email', '')}"); y -= 20
        if purchase_data.get('password'):
            c.drawString(50, y, f"Senha: {purchase_data.get('password', '')}"); y -= 20
        
        y -= 20
        c.line(50, y, 550, y)
        y -= 30
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "TERMOS E CONDIÇÕES")
        c.setFont("Helvetica", 10)
        y -= 20
        c.drawString(50, y, "• Este comprovante é válido como garantia do produto."); y -= 15
        c.drawString(50, y, "• Em caso de problemas, entre em contato com o suporte."); y -= 15
        c.drawString(50, y, "• Guarde este comprovante para referência futura."); y -= 15
        
        c.save()
        buf.seek(0)
        return buf
    
    @staticmethod
    def generate_receipt(user_id, amount, pix_id):
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, 800, "COMPROVANTE DE RECARGA")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, 770, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        c.drawString(50, 750, f"Cliente ID: {user_id}")
        c.drawString(50, 730, f"Valor: R$ {amount:.2f}")
        c.drawString(50, 710, f"ID PIX: {pix_id}")
        
        c.line(50, 690, 550, 690)
        
        c.setFont("Helvetica", 10)
        c.drawString(50, 670, "Recarga realizada via PIX - Mercado Pago")
        c.drawString(50, 655, "Este comprovante é válido como declaração de crédito.")
        
        c.save()
        buf.seek(0)
        return buf

invoice_handler = InvoiceHandler()
