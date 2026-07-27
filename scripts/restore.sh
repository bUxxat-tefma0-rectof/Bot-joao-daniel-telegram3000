#!/bin/bash

BACKUP_DIR="backups"
DB_PATH="database/bot.db"

echo "Backups disponiveis:"
ls -1 $BACKUP_DIR/backup_*.db 2>/dev/null

echo ""
echo "Digite o nome do arquivo de backup:"
read BACKUP_FILE

if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    cp "$BACKUP_DIR/$BACKUP_FILE" "$DB_PATH"
    echo "Banco restaurado com sucesso!"
else
    echo "Arquivo nao encontrado!"
fi
