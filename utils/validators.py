import re

def validate_phone(phone):
    phone = re.sub(r'\D', '', phone)
    return 10 <= len(phone) <= 13

def validate_email(email):
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None

def validate_amount(amount, min_val=0, max_val=100000):
    try:
        amount = float(amount)
        return min_val <= amount <= max_val
    except:
        return False

def validate_pix_code(code):
    return len(code) >= 50

def sanitize_html(text):
    return text.replace('<', '&lt;').replace('>', '&gt;')

def truncate_text(text, max_length=100):
    if len(text) > max_length:
        return text[:max_length-3] + '...'
    return text

def generate_id():
    import uuid
    return uuid.uuid4().hex[:16]

def format_currency(value):
    return f"R$ {float(value):.2f}"

def format_date(date):
    return date.strftime('%d/%m/%Y') if date else 'N/A'

def format_datetime(date):
    return date.strftime('%d/%m/%Y %H:%M') if date else 'N/A'

def is_valid_url(url):
    import validators
    return validators.url(url) if url else False

def mask_email(email):
    if '@' in email:
        parts = email.split('@')
        return parts[0][:2] + '***@' + parts[1]
    return email
