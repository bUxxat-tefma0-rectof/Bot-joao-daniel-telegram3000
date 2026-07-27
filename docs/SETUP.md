# Guia de Instalação

## Requisitos
- Python 3.8+
- pip
- Git

## Instalação

### 1. Clone o repositório
git clone https://github.com/SEU_USER/SEU_REPO.git
cd SEU_REPO

### 2. Instale dependências
pip install -r requirements.txt

### 3. Configure o .env
BOT_TOKEN=SEU_TOKEN
ADMIN_ID=SEU_ID
MERCADO_PAGO_ACCESS_TOKEN=SEU_TOKEN_MP
DATABASE_URL=sqlite:///database/bot.db

### 4. Inicialize banco
python database/models.py

### 5. Execute
python run.py

## Deploy no Render
- Build: pip install -r requirements.txt && mkdir -p database logs backups
- Start: python run.py
- Tipo: Worker
