#!/bin/bash

echo "ATENCAO: Isso vai resetar todo o banco de dados!"
echo "Tem certeza? (s/n)"
read CONFIRM

if [ "$CONFIRM" != "s" ]; then
    echo "Cancelado."
    exit 0
fi

echo "Parando bot..."
pkill -f "python run.py" 2>/dev/null
sleep 2

echo "Removendo banco de dados..."
rm -f database/bot.db

echo "Criando novo banco..."
python database/models.py

echo "Banco resetado com sucesso!"
echo "Inicie o bot novamente: python run.py"
