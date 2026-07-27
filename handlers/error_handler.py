from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger
import traceback

class ErrorHandler:
    @staticmethod
    async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Erro: {context.error}")
        
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = ''.join(tb_list)
        logger.error(tb_string)
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ Ocorreu um erro inesperado. Tente novamente mais tarde."
                )
            except:
                pass
    
    @staticmethod
    async def handle_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "⏰ Tempo esgotado! A operação foi cancelada."
                )
            except:
                pass
    
    @staticmethod
    async def handle_blocked_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.warning(f"Usuário bloqueado tentou interagir")
    
    @staticmethod
    async def handle_flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update and update.effective_user:
            from database.db_manager import DBManager
            db = DBManager()
            seconds = db.get_setting('flood_seconds', '6')
            db.close()
            
            try:
                await update.message.reply_text(
                    f"⚠️ Pare de floodar! Aguarde {seconds} segundos."
                )
            except:
                pass

error_handler = ErrorHandler()
