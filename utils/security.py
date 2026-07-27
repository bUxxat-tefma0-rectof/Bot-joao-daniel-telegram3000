import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
import os

class Security:
    @staticmethod
    def hash_text(text):
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def hash_md5(text):
        return hashlib.md5(text.encode()).hexdigest()
    
    @staticmethod
    def generate_token(length=32):
        import secrets
        return secrets.token_hex(length)
    
    @staticmethod
    def encrypt(text, key=None):
        if not key:
            key = Fernet.generate_key()
        f = Fernet(key)
        encrypted = f.encrypt(text.encode())
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt(encrypted_text, key):
        f = Fernet(key)
        decrypted = f.decrypt(base64.b64decode(encrypted_text))
        return decrypted.decode()
    
    @staticmethod
    def mask_sensitive(text, visible_chars=4):
        if len(text) <= visible_chars:
            return '*' * len(text)
        return text[:visible_chars] + '*' * (len(text) - visible_chars)
    
    @staticmethod
    def validate_signature(payload, signature, secret):
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    @staticmethod
    def sanitize_input(text):
        import re
        text = re.sub(r'[<>&\'"]', '', text)
        return text.strip()
    
    @staticmethod
    def generate_password(length=12):
        import secrets, string
        chars = string.ascii_letters + string.digits + '!@#$%&*'
        return ''.join(secrets.choice(chars) for _ in range(length))

security = Security()
