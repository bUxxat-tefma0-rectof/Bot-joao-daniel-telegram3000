import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config.settings import BOT_TOKEN, ADMIN_ID
from database.models import init_db
from database.db_manager import DBManager

from handlers.client_handler import start, callback, handle_msg, waiting, db as cdb
from handlers.admin_handler import admin, adm_callback, admin_states
from handlers.payment_handler import process_payment, check_pix_callback
from handlers.cart_handler import add_to_cart, view_cart, remove_from_cart, clear_cart, checkout
from handlers.search_handler import start_search, do_search
from handlers.notification_handler import toggle_alert, check_alerts
from handlers.coupon_handler import create_coupon, apply_coupon
from handlers.faq_handler import show_faq, show_faq_detail, add_faq
from handlers.backup_handler import backup_handler
from handlers.export_handler import export_users_csv, export_sales_csv, export_full_report
from handlers.support_handler import open_ticket, close_ticket, ticket_status
from handlers.referral_handler import process_referral, get_referral_stats, claim_commission
from handlers.gift_handler import redeem_gift_start, redeem_gift_process, create_gift_admin, list_gifts
from handlers.broadcast_handler import start_broadcast, start_broadcast_photo, execute_broadcast_text, execute_broadcast_photo
from handlers.stock_handler import view_stock, add_stock, remove_stock, stock_detail
from handlers.ranking_handler import show_rankings, show_ranking_detail
from handlers.conversion_handler import start_conversion, process_conversion
from handlers.rental_handler import show_rental_menu, create_tenant, list_tenants, manage_tenant
from handlers.command_handler import (
    cmd_start, cmd_admin, cmd_pix, cmd_saldo, cmd_id,
    cmd_historico, cmd_ranking, cmd_termos, cmd_suporte,
    cmd_alertas, cmd_afiliados, cmd_gift, cmd_pesquisar
)
from handlers.error_handler import error_handler
from handlers.scheduler_handler import SchedulerHandler
from handlers.payment_checker import PaymentChecker

from services.pix_service import PixService
from services.gift_service import GiftService
from services.login_service import LoginService
from services.affiliate_service import AffiliateService

from utils.logger import logger
from utils.cache import cache_handler
from middleware.auth import AuthMiddleware
from middleware.rate_limit import rate_limiter
from api.rest_api import run_api
from api.webhook_handler import run_webhook

import threading

class Bot:
    def __init__(self):
        self.db = DBManager()
        self.app = None
        self.scheduler = None
        self.payment_checker = None
    
    def setup_handlers(self):
        self.app.add_handler(CommandHandler('start', cmd_start))
        self.app.add_handler(CommandHandler('admin', cmd_admin))
        self.app.add_handler(CommandHandler('pix', cmd_pix))
        self.app.add_handler(CommandHandler('saldo', cmd_saldo))
        self.app.add_handler(CommandHandler('id', cmd_id))
        self.app.add_handler(CommandHandler('historico', cmd_historico))
        self.app.add_handler(CommandHandler('ranking', cmd_ranking))
        self.app.add_handler(CommandHandler('termos', cmd_termos))
        self.app.add_handler(CommandHandler('suporte', cmd_suporte))
        self.app.add_handler(CommandHandler('alertas', cmd_alertas))
        self.app.add_handler(CommandHandler('afiliados', cmd_afiliados))
        self.app.add_handler(CommandHandler('gift', cmd_gift))
        self.app.add_handler(CommandHandler('pesquisar', cmd_pesquisar))
        
        self.app.add_handler(CallbackQueryHandler(adm_callback, pattern='^adm_'))
        self.app.add_handler(CallbackQueryHandler(check_pix_callback, pattern='^(check_pix_|copy_pix_)'))
        self.app.add_handler(CallbackQueryHandler(remove_from_cart, pattern='^cart_remove_'))
        self.app.add_handler(CallbackQueryHandler(clear_cart, pattern='^cart_clear$'))
        self.app.add_handler(CallbackQueryHandler(checkout, pattern='^cart_checkout$'))
        self.app.add_handler(CallbackQueryHandler(start_search, pattern='^search_start$'))
        self.app.add_handler(CallbackQueryHandler(show_faq, pattern='^show_faq$'))
        self.app.add_handler(CallbackQueryHandler(show_faq_detail, pattern='^faq_'))
        self.app.add_handler(CallbackQueryHandler(start_conversion, pattern='^convert$'))
        self.app.add_handler(CallbackQueryHandler(redeem_gift_start, pattern='^gift_redeem$'))
        self.app.add_handler(CallbackQueryHandler(list_gifts, pattern='^gift_list$'))
        self.app.add_handler(CallbackQueryHandler(show_rankings, pattern='^m5$'))
        self.app.add_handler(CallbackQueryHandler(show_ranking_detail, pattern='^rank_'))
        self.app.add_handler(CallbackQueryHandler(toggle_alert, pattern='^alert_'))
        self.app.add_handler(CallbackQueryHandler(start_broadcast, pattern='^broadcast_text$'))
        self.app.add_handler(CallbackQueryHandler(start_broadcast_photo, pattern='^broadcast_photo$'))
        self.app.add_handler(CallbackQueryHandler(show_rental_menu, pattern='^rental_menu$'))
        self.app.add_handler(CallbackQueryHandler(create_tenant, pattern='^rental_create$'))
        self.app.add_handler(CallbackQueryHandler(list_tenants, pattern='^rental_list$'))
        self.app.add_handler(CallbackQueryHandler(manage_tenant, pattern='^rental_manage$'))
        self.app.add_handler(CallbackQueryHandler(callback, pattern='^(m[1-8]|cat_|prod_|buy_|multi_|pixbuy_|back|recarga_pix|history|none)$'))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_all_messages))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photos))
        self.app.add_error_handler(error_handler.handle_error)
    
    async def handle_all_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        text = update.message.text
        
        maintenance = self.db.get_setting('maintenance_mode', 'off')
        if maintenance == 'on' and user.id != ADMIN_ID:
            await update.message.reply_text("🔧 Bot em manutenção!")
            return
        
        if self.db.check_flood(user.id):
            seconds = self.db.get_setting('flood_seconds', '6')
            await update.message.reply_text(f"⚠️ Aguarde {seconds}s!")
            return
        
        if user.id == ADMIN_ID and user.id in admin_states:
            await self.handle_admin_states(update, context)
            return
        
        if user.id in waiting:
            await self.handle_user_states(update, context)
            return
        
        await handle_msg(update, context)
    
    async def handle_admin_states(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        from handlers.admin_handler import handle_admin_message
        await handle_admin_message(update, context)
    
    async def handle_user_states(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        text = update.message.text
        state = waiting[user.id]
        
        if state == 'recharge_value':
            try:
                amount = float(text)
                mn = float(self.db.get_setting('deposit_min', '2'))
                mx = float(self.db.get_setting('deposit_max', '150'))
                if amount < mn: await update.message.reply_text(f"❌ Mín R$ {mn:.2f}")
                elif amount > mx: await update.message.reply_text(f"❌ Máx R$ {mx:.2f}")
                else:
                    await update.message.reply_text("⏳ Gerando...")
                    from handlers.client_handler import gen_pix
                    await gen_pix(update.message, user, amount, self.db.get_balance(user.id))
            except: await update.message.reply_text("❌ Inválido!")
            del waiting[user.id]
        
        elif state.startswith('multi_'):
            try:
                qty = int(text)
                pid = int(state.replace('multi_', ''))
                p = self.db.get_product(pid)
                bal = self.db.get_balance(user.id)
                total = p.price * qty
                if qty > p.stock: await update.message.reply_text(f"❌ Estoque: {p.stock}")
                elif bal < total:
                    falta = total - bal
                    kb = [[InlineKeyboardButton(f"Gerar PIX R$ {total:.2f}", callback_data=f'pixbuy_{total}')]]
                    await update.message.reply_text(f"❌ Falta R$ {falta:.2f}", reply_markup=InlineKeyboardMarkup(kb))
                else:
                    for _ in range(qty):
                        self.db.subtract_balance(user.id, p.price)
                        self.db.decrease_stock(pid)
                    await update.message.reply_text(f"✅ {qty}x {p.name}")
            except: await update.message.reply_text("❌ Inválido!")
            del waiting[user.id]
        
        elif state == 'convert_points':
            try:
                pts = int(text)
                db_user = self.db.get_user(user.id)
                mult = float(self.db.get_setting('affiliate_multiplier', '0.01'))
                if pts <= db_user.affiliate_points:
                    val = pts * mult
                    db_user.affiliate_points -= pts
                    db_user.balance += val
                    self.db.db.commit()
                    await update.message.reply_text(f"✅ R$ {val:.2f}")
                else: await update.message.reply_text("❌ Pontos insuficientes!")
            except: await update.message.reply_text("❌ Inválido!")
            del waiting[user.id]
        
        elif state == 'gift_code':
            gs = GiftService()
            if gs.redeem(text.strip().upper(), user.id):
                await update.message.reply_text(f"✅ Resgatado! Saldo: R$ {self.db.get_balance(user.id):.2f}")
            else: await update.message.reply_text("❌ Inválido!")
            gs.close()
            del waiting[user.id]
        
        elif state == 'edit_whatsapp':
            db_user = self.db.get_user(user.id)
            if text.lower() == 'remover': db_user.whatsapp = None
            else: db_user.whatsapp = text
            self.db.db.commit()
            await update.message.reply_text("✅ Salvo!")
            del waiting[user.id]
    
    async def handle_photos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id == ADMIN_ID and user.id in admin_states:
            field = admin_states[user.id]
            if field == 'welcome_image':
                photo = update.message.photo[-1]
                file = await context.bot.get_file(photo.file_id)
                file_path = f"images/welcome_{user.id}.jpg"
                import os
                os.makedirs('images', exist_ok=True)
                await file.download_to_drive(file_path)
                self.db.set_setting('welcome_image', file_path)
                await update.message.reply_text("✅ Imagem salva!")
                del admin_states[user.id]
    
    def start_services(self):
        import threading
        
        api_thread = threading.Thread(target=run_api, kwargs={'port': 5000}, daemon=True)
        api_thread.start()
        
        webhook_thread = threading.Thread(target=run_webhook, kwargs={'port': 5001}, daemon=True)
        webhook_thread.start()
        
        self.scheduler = SchedulerHandler(self.app.bot)
        self.scheduler.start_all_jobs()
        
        self.payment_checker = PaymentChecker(self.app.bot)
    
    def run(self):
        print("🐕 INICIANDO BOT...")
        print("📦 Inicializando banco de dados...")
        init_db()
        print("✅ Banco de dados pronto!")
        
        print("🔧 Configurando handlers...")
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        print("✅ Handlers configurados!")
        
        print("🔗 Iniciando serviços...")
        self.start_services()
        print("✅ Serviços iniciados!")
        
        print("🚀 Bot online!")
        logger.info("Bot iniciado com sucesso")
        
        self.app.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False)

if __name__ == '__main__':
    bot = Bot()
    bot.run()
