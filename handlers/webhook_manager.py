import requests
from config.settings import MP_ACCESS_TOKEN

class WebhookManager:
    def __init__(self):
        self.mp_token = MP_ACCESS_TOKEN
        self.base_url = "https://api.mercadopago.com/v1"
    
    def create_webhook(self, url, topics=None):
        if not topics:
            topics = ['payment']
        
        headers = {
            "Authorization": f"Bearer {self.mp_token}",
            "Content-Type": "application/json"
        }
        
        for topic in topics:
            data = {
                "url": url,
                "topics": [topic]
            }
            try:
                requests.post(f"{self.base_url}/webhooks", json=data, headers=headers)
            except:
                pass
    
    def list_webhooks(self):
        headers = {"Authorization": f"Bearer {self.mp_token}"}
        try:
            response = requests.get(f"{self.base_url}/webhooks", headers=headers)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def delete_webhook(self, webhook_id):
        headers = {"Authorization": f"Bearer {self.mp_token}"}
        try:
            requests.delete(f"{self.base_url}/webhooks/{webhook_id}", headers=headers)
        except:
            pass
    
    def update_webhook_url(self, new_url):
        webhooks = self.list_webhooks()
        for wh in webhooks:
            self.delete_webhook(wh.get('id'))
        self.create_webhook(new_url)

webhook_manager = WebhookManager()
