#!/bin/bash

BACKUP_DIR="backups"
DB_PATH="database/bot.db"

mkdir -p $BACKUP_DIR

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.db"

if [ -f "$DB_PATH" ]; then
    cp "$DB_PATH" "$BACKUP_FILE"
    echo "Backup criado: $BACKUP_FILE"
else
    echo "Banco nao encontrado!"
    exit 1
fi

cd $BACKUP_DIR
ls -t backup_*.db | tail -n +11 | xargs -r rm
echo "Backups antigos removidos"
