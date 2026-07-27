from functools import wraps
from config.settings import ADMIN_ID
from database.db_manager import DBManager
from datetime import datetime
import time

db = DBManager()

def admin_only(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        if user.id != ADMIN_ID:
            await update.message.reply_text("❌ Acesso negado!")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def registered_only(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        if not db.get_user(user.id):
            await update.message.reply_text("❌ Usuário não registrado!")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def maintenance_check(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        maintenance = db.get_setting('maintenance_mode', 'off')
        if maintenance == 'on' and user.id != ADMIN_ID:
            await update.message.reply_text("🔧 Bot em manutenção!")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def flood_control(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        if db.check_flood(user.id):
            seconds = db.get_setting('flood_seconds', '6')
            await update.message.reply_text(f"⚠️ Aguarde {seconds} segundos!")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def log_action(action):
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user = update.effective_user
            start = time.time()
            result = await func(update, context, *args, **kwargs)
            elapsed = time.time() - start
            db.add_log(action, user.id, f"Tempo: {elapsed:.2f}s")
            return result
        return wrapper
    return decorator

def cache_response(ttl=300):
    def decorator(func):
        cache = {}
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                value, timestamp = cache[key]
                if time.time() - timestamp < ttl:
                    return value
            result = await func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator
