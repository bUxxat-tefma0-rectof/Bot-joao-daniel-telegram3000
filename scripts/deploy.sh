#!/bin/bash

echo "Iniciando deploy..."

echo "Atualizando codigo..."
git pull origin main

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Inicializando banco..."
python database/models.py

echo "Reiniciando bot..."
pkill -f "python run.py" 2>/dev/null
sleep 2

echo "Iniciando bot..."
nohup python run.py > logs/bot.log 2>&1 &

echo "Deploy concluido!"
