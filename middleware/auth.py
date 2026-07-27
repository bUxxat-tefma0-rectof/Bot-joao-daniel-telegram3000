from functools import wraps
from config.settings import ADMIN_ID
from database.db_manager import DBManager

db = DBManager()

class AuthMiddleware:
    @staticmethod
    def admin_only(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user = update.effective_user
            if user.id != ADMIN_ID:
                await update.message.reply_text("❌ Acesso restrito a administradores!")
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def owner_only(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user = update.effective_user
            db_user = db.get_user(user.id)
            if not db_user or not db_user.is_owner:
                await update.message.reply_text("❌ Acesso restrito ao dono!")
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def registered_only(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user = update.effective_user
            if not db.get_user(user.id):
                db.create_user(user.id, user.username, user.first_name)
            return await func(update, context, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def maintenance_check(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user = update.effective_user
            maintenance = db.get_setting('maintenance_mode', 'off')
            if maintenance == 'on' and user.id != ADMIN_ID:
                await update.message.reply_text("🔧 Bot em manutenção! Volte mais tarde.")
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
