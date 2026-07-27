import os
from datetime import datetime

class Logger:
    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def _write(self, level, message, user_id=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        uid = f"[UID:{user_id}] " if user_id else ""
        log_line = f"[{timestamp}] [{level}] {uid}{message}\n"
        
        date = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.log_dir, f'bot_{date}.log')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        print(log_line.strip())
    
    def info(self, message, user_id=None):
        self._write('INFO', message, user_id)
    
    def error(self, message, user_id=None):
        self._write('ERROR', message, user_id)
    
    def warning(self, message, user_id=None):
        self._write('WARN', message, user_id)
    
    def debug(self, message, user_id=None):
        self._write('DEBUG', message, user_id)
    
    def transaction(self, user_id, action, amount):
        message = f"Action: {action} | Amount: R$ {amount:.2f}"
        self._write('TRANSACTION', message, user_id)
    
    def admin_action(self, user_id, action):
        message = f"Admin Action: {action}"
        self._write('ADMIN', message, user_id)
    
    def purchase(self, user_id, product, amount):
        message = f"Purchase: {product} | Amount: R$ {amount:.2f}"
        self._write('PURCHASE', message, user_id)
    
    def pix(self, user_id, pix_id, amount):
        message = f"PIX: {pix_id} | Amount: R$ {amount:.2f}"
        self._write('PIX', message, user_id)
    
    def get_logs(self, date=None):
        if not date: date = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(self.log_dir, f'bot_{date}.log')
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                return f.read()
        return "Nenhum log encontrado."
    
    def clean_old_logs(self, days=30):
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        for filename in os.listdir(self.log_dir):
            if filename.startswith('bot_') and filename.endswith('.log'):
                file_path = os.path.join(self.log_dir, filename)
                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_date < cutoff:
                    os.remove(file_path)

logger = Logger()
