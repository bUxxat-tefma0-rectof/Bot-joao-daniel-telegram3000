from datetime import datetime, timedelta
import pytz

class DateUtils:
    @staticmethod
    def now():
        return datetime.now()
    
    @staticmethod
    def today():
        return datetime.now().date()
    
    @staticmethod
    def format_date(date, fmt='%d/%m/%Y'):
        if isinstance(date, str):
            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        return date.strftime(fmt)
    
    @staticmethod
    def format_datetime(date, fmt='%d/%m/%Y %H:%M'):
        if isinstance(date, str):
            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        return date.strftime(fmt)
    
    @staticmethod
    def add_days(date, days):
        return date + timedelta(days=days)
    
    @staticmethod
    def add_hours(date, hours):
        return date + timedelta(hours=hours)
    
    @staticmethod
    def add_minutes(date, minutes):
        return date + timedelta(minutes=minutes)
    
    @staticmethod
    def days_between(date1, date2):
        return abs((date2 - date1).days)
    
    @staticmethod
    def is_expired(date):
        return date < datetime.now()
    
    @staticmethod
    def start_of_month():
        return datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def end_of_month():
        next_month = datetime.now().replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)
    
    @staticmethod
    def start_of_day():
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def end_of_day():
        return datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def to_timezone(date, timezone='America/Sao_Paulo'):
        tz = pytz.timezone(timezone)
        if date.tzinfo is None:
            date = pytz.UTC.localize(date)
        return date.astimezone(tz)
    
    @staticmethod
    def relative_time(date):
        now = datetime.now()
        diff = now - date
        
        if diff.days > 365:
            return f"{diff.days // 365} anos atrás"
        elif diff.days > 30:
            return f"{diff.days // 30} meses atrás"
        elif diff.days > 0:
            return f"{diff.days} dias atrás"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} horas atrás"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minutos atrás"
        else:
            return "agora mesmo"

date_utils = DateUtils()
