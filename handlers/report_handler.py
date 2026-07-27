from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from datetime import datetime
from database.db_manager import DBManager

db = DBManager()

class ReportHandler:
    @staticmethod
    def generate_daily_report():
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, 800, f"RELATÓRIO DIÁRIO")
        c.setFont("Helvetica", 12)
        c.drawString(50, 780, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
        
        stats = db.get_stats()
        y = 750
        
        data = [
            ['Métrica', 'Valor'],
            ['Usuários', str(stats['users'])],
            ['Produtos Ativos', str(stats['products'])],
            ['Vendas Hoje', str(stats['today_sales'])],
            ['Receita Hoje', f"R$ {stats['today_revenue']:.2f}"],
            ['Receita Total', f"R$ {stats['total_revenue']:.2f}"],
            ['Recargas', str(stats['total_recharges'])],
            ['Estoque Logins', str(stats['logins_stock'])],
        ]
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        table.wrapOn(c, 500, 600)
        table.drawOn(c, 50, 600)
        
        c.save()
        buf.seek(0)
        return buf
    
    @staticmethod
    def generate_monthly_report():
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, 800, f"RELATÓRIO MENSAL")
        c.setFont("Helvetica", 12)
        c.drawString(50, 780, f"Mês: {datetime.now().strftime('%m/%Y')}")
        
        from handlers.analytics_handler import analytics_handler
        stats = analytics_handler.get_monthly_stats()
        
        y = 750
        c.drawString(50, y, f"Novos usuários: {stats['users']}"); y -= 20
        c.drawString(50, y, f"Vendas: {stats['sales']}"); y -= 20
        c.drawString(50, y, f"Receita: R$ {stats['revenue']:.2f}"); y -= 20
        c.drawString(50, y, f"Ticket médio: R$ {stats['avg_ticket']:.2f}")
        
        c.save()
        buf.seek(0)
        return buf

report_handler = ReportHandler()
