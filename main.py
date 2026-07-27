import asyncio
from telegram import Updatefrom telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config.settings import BOT_TOKEN, ADMIN_ID
from database.models import init_db
from handlers.client_handler import start, callback, handle_msg, waiting, db as cdb
from handlers.admin_handler import admin, adm_callback, astates
from scheduler.jobs import Scheduler

async def handle_admin_msg(update,context):
    u=update.effective_user; txt=update.message.text
    if u.id==ADMIN_ID and u.id in astates:
        field=astates[u.id]
        fm={'welcome':'welcome_text','image':'welcome_image','support':'support_link','catalog_text':'catalog_text','product_text':'product_text','insufficient_text':'insufficient_text','pix_result_text':'pix_result_text','profile_text':'profile_text','recarga_text':'recarga_text','pix_ask_text':'pix_ask_text','multi_text':'multi_text','convert_text':'convert_text','success_text':'success_text','history_text':'history_text','terms_text':'terms_text','support_text':'support_text','flood_text':'flood_text','expired_pix_text':'expired_pix_text','btn1':'btn1_text','btn2':'btn2_text','btn3':'btn3_text','btn4':'btn4_text','btn5':'btn5_text','btn6':'btn6_text','btn7':'btn7_text','btn8':'btn8_text','mp_token':'mp_access_token','deposit_min':'deposit_min','deposit_max':'deposit_max','expiration':'pix_expiration','bonus':'bonus_percentage','bonus_min':'bonus_min_value','commission':'commission_percentage','affiliate_points':'affiliate_points_per_recharge','affiliate_min_points':'affiliate_min_points','registration_bonus':'registration_bonus','flood_seconds':'flood_seconds'}
        if field=='pos':
            for i,p in enumerate(txt.split('|')[:8],1):
                if p.strip() in ['full','left','right']: cdb.set_setting(f'btn{i}_pos',p.strip())
            await update.message.reply_text("✅")
        elif field=='broadcast':
            from database.models import SessionLocal, User
            s=SessionLocal(); users=s.query(User).all(); c=0
            for uu in users:
                try: await context.bot.send_message(uu.telegram_id,txt); c+=1
                except: pass
            s.close(); await update.message.reply_text(f"✅ {c}")
        elif field=='add_product':
            p=txt.split('|')
            if len(p)>=3: cdb.add_product(p[0].strip(),float(p[1]),int(p[2]),p[3].strip() if len(p)>3 else '')
            await update.message.reply_text("✅")
        elif field=='gift':
            try:
                from services.gift_service import GiftService; gs=GiftService()
                g=gs.create(float(txt)); await update.message.reply_text(f"✅ {g.code}"); gs.close()
            except: await update.message.reply_text("❌")
        elif field=='add_login':
            p=txt.split('|')
            if len(p)>=3:
                from services.login_service import LoginService; ls=LoginService()
                ls.add(p[0].strip(),p[1].strip(),p[2].strip(),p[3].strip() if len(p)>3 else '',p[4].strip() if len(p)>4 else '30 dias',float(p[5]) if len(p)>5 else 0)
                ls.close(); await update.message.reply_text("✅")
        elif field=='remove_login':
            from services.login_service import LoginService; ls=LoginService()
            c=ls.remove(txt.strip()); await update.message.reply_text(f"✅ {c}"); ls.close()
        elif field=='remove_platform':
            from services.login_service import LoginService; ls=LoginService()
            c=ls.remove(txt.strip()); await update.message.reply_text(f"✅ {c}"); ls.close()
        elif field=='clear_stock':
            if txt.upper()=='CONFIRMAR':
                from services.login_service import LoginService; ls=LoginService()
                c=ls.clear(); await update.message.reply_text(f"✅ {c}"); ls.close()
        elif field=='service_price':
            p=txt.split('|')
            if len(p)>=2:
                from services.login_service import LoginService; ls=LoginService()
                c=ls.update_price(p[0].strip(),float(p[1])); await update.message.reply_text(f"✅ {c}"); ls.close()
        elif field=='all_prices':
            try:
                from services.login_service import LoginService; ls=LoginService()
                c=ls.update_all(float(txt)); await update.message.reply_text(f"✅ {c}"); ls.close()
            except: await update.message.reply_text("❌")
        elif field=='add_admin':
            try:
                from database.models import SessionLocal, User
                s=SessionLocal(); u=s.query(User).filter_by(telegram_id=int(txt)).first()
                if u: u.is_admin=True; s.commit(); await update.message.reply_text("✅")
                else: await update.message.reply_text("❌")
                s.close()
            except: await update.message.reply_text("❌")
        elif field=='remove_admin':
            try:
                from database.models import SessionLocal, User
                s=SessionLocal(); u=s.query(User).filter_by(telegram_id=int(txt)).first()
                if u: u.is_admin=False; s.commit(); await update.message.reply_text("✅")
                else: await update.message.reply_text("❌")
                s.close()
            except: await update.message.reply_text("❌")
        elif field=='search_user':
            try:
                u=cdb.get_user(int(txt))
                if u: await update.message.reply_text(f"👤 {u.telegram_id}\n💰 R$ {u.balance:.2f}\n🛒 {u.total_purchases}")
                else: await update.message.reply_text("❌")
            except: await update.message.reply_text("❌")
        elif field in fm: cdb.set_setting(fm[field],txt); await update.message.reply_text("✅")
        else: await update.message.reply_text("✅")
        del astates[u.id]; return
    await handle_msg(update,context)

def main():
    print("🐕 INICIANDO..."); init_db(); print("✅ Pronto!")
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start',start))
    app.add_handler(CommandHandler('admin',admin))
    app.add_handler(CallbackQueryHandler(callback,pattern='^(?!adm_).*'))
    app.add_handler(CallbackQueryHandler(adm_callback,pattern='^adm_'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_admin_msg))
    s=Scheduler(app.bot); s.start()
    print("✅ Online!"); app.run_polling(allowed_updates=Update.ALL_TYPES,close_loop=False)

if __name__=='__main__': main()
