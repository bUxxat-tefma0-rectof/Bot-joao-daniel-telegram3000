import os
import shutil
from datetime import datetime
from database.db_manager import DBManager

db = DBManager()

class BackupHandler:
    def __init__(self):
        self.backup_dir = 'backups'
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_path = os.environ.get('DATABASE_URL', 'database/bot.db')
        
        if db_path.startswith('sqlite:///'):
            db_path = db_path.replace('sqlite:///', '')
        
        if os.path.exists(db_path):
            backup_file = os.path.join(self.backup_dir, f'backup_{timestamp}.db')
            shutil.copy2(db_path, backup_file)
            self.clean_old_backups()
            return backup_file
        return None
    
    def clean_old_backups(self, keep=10):
        files = sorted([f for f in os.listdir(self.backup_dir) if f.startswith('backup_')], reverse=True)
        for f in files[keep:]:
            os.remove(os.path.join(self.backup_dir, f))
    
    def restore_backup(self, backup_file):
        db_path = os.environ.get('DATABASE_URL', 'database/bot.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path.replace('sqlite:///', '')
        
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, db_path)
            return True
        return False
    
    def list_backups(self):
        files = sorted([f for f in os.listdir(self.backup_dir) if f.startswith('backup_')], reverse=True)
        return files

backup_handler = BackupHandler()
