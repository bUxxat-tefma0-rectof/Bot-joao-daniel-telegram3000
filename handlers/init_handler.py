from database.models import init_db
from handlers.client_handler import start, callback, handle_msg
from handlers.admin_handler import admin, adm_callback
from handlers.payment_handler import check_pix_callback
from handlers.cart_handler import add_to_cart, view_cart, remove_from_cart, clear_cart, checkout
from handlers.search_handler import start_search, do_search
from handlers.conversion_handler import start_conversion, process_conversion
from handlers.gift_handler import redeem_gift_start, redeem_gift_process
from handlers.ranking_handler import show_rankings, show_ranking_detail
from handlers.stock_handler import view_stock
from handlers.broadcast_handler import start_broadcast, execute_broadcast_text
from handlers.referral_handler import process_referral, get_referral_stats
from handlers.faq_handler import show_faq, show_faq_detail
from handlers.coupon_handler import create_coupon, apply_coupon
from handlers.support_handler import open_ticket, close_ticket
from handlers.notification_handler import toggle_alert, check_alerts
from handlers.export_handler import export_users_csv, export_sales_csv
from handlers.rental_handler import show_rental_menu, create_tenant, list_tenants
from handlers.command_handler import (
    cmd_start, cmd_admin, cmd_pix, cmd_saldo, cmd_id,
    cmd_historico, cmd_ranking, cmd_termos, cmd_suporte,
    cmd_alertas, cmd_afiliados, cmd_gift, cmd_pesquisar
)
from handlers.error_handler import error_handler
from handlers.scheduler_handler import SchedulerHandler
from handlers.payment_checker import PaymentChecker

class InitHandler:
    def __init__(self, app, bot):
        self.app = app
        self.bot = bot
        
        self.register_handlers()
        self.start_schedulers()
    
    def register_handlers(self):
        from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
        
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
        self.app.add_handler(CallbackQueryHandler(callback, pattern='^(m[1-8]|cat_|prod_|buy_|multi_|pixbuy_|back|recarga_pix|convert|history|rank_|none)$'))
        self.app.add_handler(CallbackQueryHandler(show_rankings, pattern='^m5$'))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
        
        self.app.add_error_handler(error_handler.handle_error)
    
    def start_schedulers(self):
        global scheduler_handler, payment_checker
        scheduler_handler = SchedulerHandler(self.bot)
        scheduler_handler.start_all_jobs()
        payment_checker = PaymentChecker(self.bot)

def initialize_all():
    print("📦 Inicializando banco de dados...")
    init_db()
    print("✅ Banco de dados pronto!")
