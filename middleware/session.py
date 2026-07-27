from datetime import datetime, timedelta
from collections import defaultdict

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, user_id, data=None):
        self.sessions[user_id] = {
            'data': data or {},
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
    
    def get_session(self, user_id):
        if user_id in self.sessions:
            self.sessions[user_id]['last_activity'] = datetime.now()
            return self.sessions[user_id]['data']
        return None
    
    def update_session(self, user_id, data):
        if user_id in self.sessions:
            self.sessions[user_id]['data'].update(data)
            self.sessions[user_id]['last_activity'] = datetime.now()
    
    def delete_session(self, user_id):
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def clean_expired(self, minutes=30):
        cutoff = datetime.now() - timedelta(minutes=minutes)
        expired = [uid for uid, s in self.sessions.items() if s['last_activity'] < cutoff]
        for uid in expired:
            del self.sessions[uid]
    
    def is_active(self, user_id):
        if user_id in self.sessions:
            return (datetime.now() - self.sessions[user_id]['last_activity']).seconds < 300
        return False

session_manager = SessionManager()
