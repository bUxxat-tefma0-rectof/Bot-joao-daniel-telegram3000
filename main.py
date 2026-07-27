import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config.settings import BOT_TOKEN, ADMIN_ID
from database.models import init_db
from database.db_manager import DBManager

# Handlers
from handlers.client_handler import start, callback, handle_msg, waiting, db as cdb
from handlers.admin_handler import admin, adm_callback, astates
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

# Serviços
from services.pix_service import PixService
from services.gift_service import GiftService
from services.login_service import LoginService
from services.affiliate_service import AffiliateService
from services.pdf_service import PDFService

# Utilitários
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
        """Registra todos os handlers no aplicativo"""
        
        # Comandos principais
        self.app.add_handler(CommandHandler('start', cmd_start))
        self.app.add_handler(CommandHandler('admin', cmd_admin))
        
        # Comandos do usuário
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
        
        # Callbacks do admin
        self.app.add_handler(CallbackQueryHandler(adm_callback, pattern='^adm_'))
        
        # Callbacks de pagamento
        self.app.add_handler(CallbackQueryHandler(check_pix_callback, pattern='^(check_pix_|copy_pix_)'))
        
        # Callbacks do carrinho
        self.app.add_handler(CallbackQueryHandler(remove_from_cart, pattern='^cart_remove_'))
        self.app.add_handler(CallbackQueryHandler(clear_cart, pattern='^cart_clear$'))
        self.app.add_handler(CallbackQueryHandler(checkout, pattern='^cart_checkout$'))
        
        # Callbacks de pesquisa
        self.app.add_handler(CallbackQueryHandler(start_search, pattern='^search_start$'))
        self.app.add_handler(CallbackQueryHandler(show_faq, pattern='^show_faq$'))
        self.app.add_handler(CallbackQueryHandler(show_faq_detail, pattern='^faq_'))
        
        # Callbacks de conversão
        self.app.add_handler(CallbackQueryHandler(start_conversion, pattern='^convert$'))
        
        # Callbacks de gift card
        self.app.add_handler(CallbackQueryHandler(redeem_gift_start, pattern='^gift_redeem$'))
        self.app.add_handler(CallbackQueryHandler(list_gifts, pattern='^gift_list$'))
        
        # Callbacks de ranking
        self.app.add_handler(CallbackQueryHandler(show_rankings, pattern='^m5$'))
        self.app.add_handler(CallbackQueryHandler(show_ranking_detail, pattern='^rank_'))
        
        # Callbacks de alertas
        self.app.add_handler(CallbackQueryHandler(toggle_alert, pattern='^alert_'))
        
        # Callbacks de broadcast
        self.app.add_handler(CallbackQueryHandler(start_broadcast, pattern='^broadcast_text$'))
        self.app.add_handler(CallbackQueryHandler(start_broadcast_photo, pattern='^broadcast_photo$'))
        
        # Callbacks de aluguel
        self.app.add_handler(CallbackQueryHandler(show_rental_menu, pattern='^rental_menu$'))
        self.app.add_handler(CallbackQueryHandler(create_tenant, pattern='^rental_create$'))
        self.app.add_handler(CallbackQueryHandler(list_tenants, pattern='^rental_list$'))
        self.app.add_handler(CallbackQueryHandler(manage_tenant, pattern='^rental_manage$'))
        
        # Callbacks do cliente (menu principal, catálogo, compra)
        self.app.add_handler(CallbackQueryHandler(callback, pattern='^(m[1-8]|cat_|prod_|buy_|multi_|pixbuy_|back|recarga_pix|history|none)$'))
        
        # Mensagens de texto
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_all_messages))
        
        # Fotos (para broadcast com foto)
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photos))
        
        # Erro handler
        self.app.add_error_handler(error_handler.handle_error)
    
    async def handle_all_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Roteador principal de mensagens"""
        user = update.effective_user
        text = update.message.text
        
        # Verificar manutenção
        maintenance = self.db.get_setting('maintenance_mode', 'off')
        if maintenance == 'on' and user.id != ADMIN_ID:
            await update.message.reply_text("🔧 Bot em manutenção! Volte mais tarde.")
            return
        
        # Verificar flood
        if self.db.check_flood(user.id):
            seconds = self.db.get_setting('flood_seconds', '6')
            await update.message.reply_text(f"⚠️ Aguarde {seconds} segundos!")
            return
        
        # Admin states (editando configurações)
        if user.id == ADMIN_ID and user.id in astates:
            await self.handle_admin_states(update, context)
            return
        
        # User states (comprando, convertendo, etc)
        if user.id in waiting:
            await self.handle_user_states(update, context)
            return
        
        # Mensagem normal -> menu principal
        await handle_msg(update, context)
    
    async def handle_admin_states(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa estados do admin (editando configurações)"""
        user = update.effective_user
        text = update.message.text
        field = astates[user.id]
        
        field_map = {
            'welcome': 'welcome_text', 'image': 'welcome_image', 'support': 'support_link',
            'catalog_text': 'catalog_text', 'product_text': 'product_text',
            'insufficient_text': 'insufficient_text', 'pix_result_text': 'pix_result_text',
            'profile_text': 'profile_text', 'recarga_text': 'recarga_text',
            'pix_ask_text': 'pix_ask_text', 'multi_text': 'multi_text',
            'convert_text': 'convert_text', 'success_text': 'success_text',
            'history_text': 'history_text', 'terms_text': 'terms_text',
            'support_text': 'support_text', 'flood_text': 'flood_text',
            'expired_pix_text': 'expired_pix_text',
            'btn1': 'btn1_text', 'btn2': 'btn2_text', 'btn3': 'btn3_text', 'btn4': 'btn4_text',
            'btn5': 'btn5_text', 'btn6': 'btn6_text', 'btn7': 'btn7_text', 'btn8': 'btn8_text',
            'mp_token': 'mp_access_token', 'deposit_min': 'deposit_min',
            'deposit_max': 'deposit_max', 'expiration': 'pix_expiration',
            'bonus': 'bonus_percentage', 'bonus_min': 'bonus_min_value',
            'commission': 'commission_percentage', 'registration_bonus': 'registration_bonus',
            'flood_seconds': 'flood_seconds', 'convert_seconds': 'convert_seconds',
        }
        
        if field == 'pos':
            for i, p in enumerate(text.split('|')[:8], 1):
                if p.strip() in ['full', 'left', 'right']:
                    self.db.set_setting(f'btn{i}_pos', p.strip())
            await update.message.reply_text("✅ Posições salvas!")
        
        elif field == 'broadcast':
            from database.models import SessionLocal, User
            session = SessionLocal()
            users = session.query(User).all()
            count = 0
            for u in users:
                try:
                    await context.bot.send_message(u.telegram_id, text)
                    count += 1
                except:
                    pass
            session.close()
            await update.message.reply_text(f"✅ Enviado para {count} usuários!")
        
        elif field == 'add_product':
            parts = text.split('|')
            if len(parts) >= 3:
                self.db.add_product(parts[0].strip(), float(parts[1]), int(parts[2]),
                                    parts[3].strip() if len(parts) > 3 else '',
                                    parts[4].strip() if len(parts) > 4 else '')
                await update.message.reply_text("✅ Produto adicionado!")
        
        elif field == 'gift':
            try:
                gs = GiftService()
                gift = gs.create(float(text))
                await update.message.reply_text(f"✅ Gift Card criado!\nCódigo: {gift.code}\nValor: R$ {text}")
                gs.close()
            except:
                await update.message.reply_text("❌ Valor inválido!")
        
        elif field == 'add_login':
            parts = text.split('|')
            if len(parts) >= 3:
                ls = LoginService()
                ls.add(parts[0].strip(), parts[1].strip(), parts[2].strip(),
                       parts[3].strip() if len(parts) > 3 else '',
                       parts[4].strip() if len(parts) > 4 else '30 dias',
                       float(parts[5]) if len(parts) > 5 else 0)
                ls.close()
                await update.message.reply_text("✅ Login adicionado!")
        
        elif field == 'remove_login':
            ls = LoginService()
            count = ls.remove(text.strip())
            ls.close()
            await update.message.reply_text(f"✅ {count} logins removidos!")
        
        elif field == 'remove_platform':
            ls = LoginService()
            count = ls.remove(text.strip())
            ls.close()
            await update.message.reply_text(f"✅ {count} logins removidos!")
        
        elif field == 'clear_stock':
            if text.upper() == 'CONFIRMAR':
                ls = LoginService()
                count = ls.clear()
                ls.close()
                await update.message.reply_text(f"✅ {count} logins removidos!")
        
        elif field == 'service_price':
            parts = text.split('|')
            if len(parts) >= 2:
                ls = LoginService()
                count = ls.update_price(parts[0].strip(), float(parts[1]))
                ls.close()
                await update.message.reply_text(f"✅ {count} logins atualizados!")
        
        elif field == 'all_prices':
            try:
                ls = LoginService()
                count = ls.update_all(float(text))
                ls.close()
                await update.message.reply_text(f"✅ {count} logins atualizados!")
            except:
                await update.message.reply_text("❌ Valor inválido!")
        
        elif field == 'add_admin':
            try:
                u = self.db.get_user(int(text))
                if u:
                    u.is_admin = True
                    self.db.db.commit()
                    await update.message.reply_text("✅ Admin adicionado!")
                else:
                    await update.message.reply_text("❌ Usuário não encontrado!")
            except:
                await update.message.reply_text("❌ ID inválido!")
        
        elif field == 'remove_admin':
            try:
                u = self.db.get_user(int(text))
                if u:
                    u.is_admin = False
                    self.db.db.commit()
                    await update.message.reply_text("✅ Admin removido!")
                else:
                    await update.message.reply_text("❌ Usuário não encontrado!")
            except:
                await update.message.reply_text("❌ ID inválido!")
        
        elif field == 'search_user':
            try:
                u = self.db.get_user(int(text))
                if u:
                    await update.message.reply_text(
                        f"👤 ID: {u.telegram_id}\n"
                        f"💰 Saldo: R$ {u.balance:.2f}\n"
                        f"🛒 Compras: {u.total_purchases}\n"
                        f"💳 Recarregado: R$ {u.total_recharged:.2f}"
                    )
                else:
                    await update.message.reply_text("❌ Não encontrado!")
            except:
                await update.message.reply_text("❌ ID inválido!")
        
        elif field in field_map:
            self.db.set_setting(field_map[field], text)
            await update.message.reply_text("✅ Salvo!")
        
        else:
            await update.message.reply_text("✅ Comando processado!")
        
        del astates[user.id]
    
    async def handle_user_states(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa estados do usuário (compras, conversão, etc)"""
        user = update.effective_user
        text = update.message.text
        state = waiting[user.id]
        
        if state == 'recharge_value':
            try:
                amount = float(text)
                mn = float(self.db.get_setting('deposit_min', '2'))
                mx = float(self.db.get_setting('deposit_max', '150'))
                
                if amount < mn:
                    await update.message.reply_text(f"❌ Valor mínimo: R$ {mn:.2f}")
                elif amount > mx:
                    await update.message.reply_text(f"❌ Valor máximo: R$ {mx:.2f}")
                else:
                    await update.message.reply_text("⏳ Gerando PIX...")
                    from handlers.client_handler import gen_pix
                    await gen_pix(update.message, user, amount, self.db.get_balance(user.id))
            except:
                await update.message.reply_text("❌ Valor inválido!")
            del waiting[user.id]
        
        elif state.startswith('multi_'):
            try:
                qty = int(text)
                pid = int(state.replace('multi_', ''))
                p = self.db.get_product(pid)
                bal = self.db.get_balance(user.id)
                total = p.price * qty
                
                if qty > p.stock:
                    await update.message.reply_text(f"❌ Estoque insuficiente! Disponível: {p.stock}")
                elif bal < total:
                    falta = total - bal
                    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                    kb = [[InlineKeyboardButton(f"Gerar PIX R$ {total:.2f}", callback_data=f'pixbuy_{total}')]]
                    await update.message.reply_text(
                        f"❌ Saldo insuficiente!\n💰 Saldo: R$ {bal:.2f}\n💵 Total: R$ {total:.2f}\n📉 Falta: R$ {falta:.2f}",
                        reply_markup=InlineKeyboardMarkup(kb)
                    )
                else:
                    for _ in range(qty):
                        self.db.subtract_balance(user.id, p.price)
                        self.db.decrease_stock(pid)
                    await update.message.reply_text(f"✅ {qty}x {p.name} comprado(s)!")
            except:
                await update.message.reply_text("❌ Valor inválido!")
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
                    await update.message.reply_text(f"✅ Convertido!\n💰 R$ {val:.2f} adicionado ao saldo!")
                else:
                    await update.message.reply_text("❌ Pontos insuficientes!")
            except:
                await update.message.reply_text("❌ Valor inválido!")
            del waiting[user.id]
        
        elif state == 'gift_code':
            gs = GiftService()
            if gs.redeem(text.strip().upper(), user.id):
                await update.message.reply_text(f"✅ Gift Card resgatado!\n💰 Saldo: R$ {self.db.get_balance(user.id):.2f}")
            else:
                await update.message.reply_text("❌ Código inválido ou já utilizado!")
            gs.close()
            del waiting[user.id]
        
        elif state == 'edit_whatsapp':
            db_user = self.db.get_user(user.id)
            if text.lower() == 'remover':
                db_user.whatsapp = None
            else:
                from utils.validators import validate_phone
                if validate_phone(text):
                    db_user.whatsapp = text
                else:
                    await update.message.reply_text("❌ Número inválido!")
                    return
            self.db.db.commit()
            await update.message.reply_text("✅ WhatsApp salvo!")
            del waiting[user.id]
        
        elif state in waiting:
            del waiting[user.id]
    
    async def handle_photos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa fotos enviadas (broadcast com foto)"""
        user = update.effective_user
        
        if user.id == ADMIN_ID and user.id in astates:
            field = astates[user.id]
            if field == 'welcome_image':
                photo = update.message.photo[-1]
                file = await context.bot.get_file(photo.file_id)
                file_path = f"images/welcome_{user.id}.jpg"
                import os
                os.makedirs('images', exist_ok=True)
                await file.download_to_drive(file_path)
                self.db.set_setting('welcome_image', file_path)
                await update.message.reply_text("✅ Imagem salva!")
                del astates[user.id]
    
    def start_services(self):
        """Inicia serviços em background"""
        # Scheduler
        self.scheduler = SchedulerHandler(self.app.bot)
        self.scheduler.start_all_jobs()
        
        # Payment checker
        self.payment_checker = PaymentChecker(self.app.bot)
        
        # API REST em thread separada
        api_thread = threading.Thread(target=run_api, kwargs={'port': 5000}, daemon=True)
        api_thread.start()
        
        # Webhook em thread separada
        webhook_thread = threading.Thread(target=run_webhook, kwargs={'port': 5001}, daemon=True)
        webhook_thread.start()
    
    def run(self):
        """Inicia o bot"""
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
