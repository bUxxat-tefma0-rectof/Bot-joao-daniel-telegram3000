import re
import unicodedata

class StringUtils:
    @staticmethod
    def remove_accents(text):
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    
    @staticmethod
    def slugify(text):
        text = StringUtils.remove_accents(text.lower())
        return re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    
    @staticmethod
    def truncate(text, max_length, suffix='...'):
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def extract_numbers(text):
        return re.sub(r'[^0-9]', '', text)
    
    @staticmethod
    def extract_letters(text):
        return re.sub(r'[^a-zA-Z]', '', text)
    
    @staticmethod
    def mask_email(email):
        if '@' in email:
            parts = email.split('@')
            return parts[0][:2] + '***@' + parts[1]
        return email
    
    @staticmethod
    def mask_phone(phone):
        if len(phone) >= 10:
            return phone[:2] + '*****' + phone[-3:]
        return phone
    
    @staticmethod
    def capitalize_words(text):
        return ' '.join(word.capitalize() for word in text.split())
    
    @staticmethod
    def remove_extra_spaces(text):
        return ' '.join(text.split())
    
    @staticmethod
    def is_valid_url(text):
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, text))
    
    @staticmethod
    def extract_urls(text):
        pattern = r'https?://[^\s]+'
        return re.findall(pattern, text)
    
    @staticmethod
    def highlight_text(text, search, highlight='*'):
        return re.sub(f'({re.escape(search)})', f'{highlight}\\1{highlight}', text, flags=re.IGNORECASE)
    
    @staticmethod
    def word_count(text):
        return len(text.split())
    
    @staticmethod
    def random_string(length=8):
        import random, string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

string_utils = StringUtils()
