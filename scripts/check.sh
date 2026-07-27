#!/bin/bash

echo "=== Verificacao do Bot ==="

echo ""
echo "Python:"
python --version 2>/dev/null || echo "Python nao encontrado!"

echo ""
echo "Pip:"
pip --version 2>/dev/null || echo "Pip nao encontrado!"

echo ""
echo "Banco de dados:"
if [ -f "database/bot.db" ]; then
    echo "Banco encontrado!"
    ls -la database/bot.db
else
    echo "Banco nao encontrado!"
fi

echo ""
echo "Arquivo .env:"
if [ -f ".env" ]; then
    echo ".env encontrado!"
else
    echo ".env nao encontrado!"
fi

echo ""
echo "Dependencias:"
pip list 2>/dev/null | grep -E "telegram|sqlalchemy|qrcode|pillow|requests|mercadopago|flask"

echo ""
echo "Logs recentes:"
tail -5 logs/bot.log 2>/dev/null || echo "Sem logs."

echo ""
echo "=== Verificacao concluida ==="
