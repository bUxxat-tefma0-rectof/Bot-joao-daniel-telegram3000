from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

class PDFService:
    @staticmethod
    def generate_history(user_data, purchases):
        buf=BytesIO()
        c=canvas.Canvas(buf,pagesize=A4)
        c.setFont("Helvetica-Bold",16); c.drawString(50,800,"Historico de Compras")
        c.setFont("Helvetica",10); y=770
        c.drawString(50,y,f"ID: {user_data.get('id','')}"); y-=15
        c.drawString(50,y,f"Nome: {user_data.get('nome','')}"); y-=15
        c.drawString(50,y,f"Saldo: R$ {user_data.get('saldo',0):.2f}"); y-=30
        c.setFont("Helvetica-Bold",12); c.drawString(50,y,"COMPRAS:"); y-=20
        c.setFont("Helvetica",9)
        for p in purchases:
            if y<100: c.showPage(); y=800
            c.drawString(50,y,f"Produto: {p.product_name}"); y-=12
            c.drawString(50,y,f"Valor: R$ {p.amount:.2f} | Data: {p.purchase_date.strftime('%d/%m/%Y')}"); y-=12
            if p.email: c.drawString(50,y,f"Email: {p.email} | Senha: {p.password}"); y-=12
            if p.expiration_date: c.drawString(50,y,f"Vencimento: {p.expiration_date.strftime('%d/%m/%Y')}"); y-=12
            y-=10
        c.save(); buf.seek(0); return buf
