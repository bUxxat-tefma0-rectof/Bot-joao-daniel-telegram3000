#!/bin/bash

echo "Limpando arquivos temporarios..."

rm -rf __pycache__
rm -rf .pytest_cache
rm -rf *.pyc
rm -rf **/*.pyc

echo "Limpando logs antigos..."
find logs/ -name "*.log" -mtime +30 -delete

echo "Limpando backups antigos..."
cd backups 2>/dev/null
ls -t backup_*.db | tail -n +11 | xargs -r rm
cd ..

echo "Limpeza concluida!"
