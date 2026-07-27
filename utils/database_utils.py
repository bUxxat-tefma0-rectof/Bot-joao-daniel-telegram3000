from database.models import SessionLocal
from sqlalchemy import text
import os
import shutil
from datetime import datetime

class DatabaseUtils:
    @staticmethod
    def get_table_counts():
        session = SessionLocal()
        tables = ['users', 'products', 'purchases', 'pix_recharges', 'gift_cards', 'logins', 'settings', 'alerts', 'logs']
        counts = {}
        for table in tables:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            counts[table] = result.scalar()
        session.close()
        return counts
    
    @staticmethod
    def optimize_database():
        session = SessionLocal()
        session.execute(text("VACUUM"))
        session.execute(text("REINDEX"))
        session.close()
        return True
    
    @staticmethod
    def get_database_size():
        db_path = os.environ.get('DATABASE_URL', 'database/bot.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path.replace('sqlite:///', '')
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            return size
        return 0
    
    @staticmethod
    def format_size(size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
    
    @staticmethod
    def repair_database():
        session = SessionLocal()
        session.execute(text("PRAGMA integrity_check"))
        session.close()
        return True
    
    @staticmethod
    def export_table(table_name, format='csv'):
        import csv, json
        from io import StringIO
        session = SessionLocal()
        result = session.execute(text(f"SELECT * FROM {table_name}"))
        columns = result.keys()
        rows = result.fetchall()
        session.close()
        
        output = StringIO()
        if format == 'csv':
            writer = csv.writer(output)
            writer.writerow(columns)
            for row in rows:
                writer.writerow(row)
        elif format == 'json':
            data = [dict(zip(columns, row)) for row in rows]
            json.dump(data, output, indent=2)
        
        return output.getvalue()
    
    @staticmethod
    def get_query_stats():
        session = SessionLocal()
        stats = {
            'total_users': session.execute(text("SELECT COUNT(*) FROM users")).scalar(),
            'active_today': session.execute(text("SELECT COUNT(*) FROM users WHERE created_at >= date('now')")).scalar(),
            'total_sales': session.execute(text("SELECT COUNT(*) FROM purchases")).scalar(),
            'total_revenue': session.execute(text("SELECT COALESCE(SUM(amount), 0) FROM purchases")).scalar(),
            'pending_pix': session.execute(text("SELECT COUNT(*) FROM pix_recharges WHERE status='pending'")).scalar(),
            'available_logins': session.execute(text("SELECT COUNT(*) FROM logins WHERE is_sold=0")).scalar(),
        }
        session.close()
        return stats

db_utils = DatabaseUtils()
