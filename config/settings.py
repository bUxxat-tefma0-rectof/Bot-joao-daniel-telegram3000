import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
MP_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database/bot.db')
