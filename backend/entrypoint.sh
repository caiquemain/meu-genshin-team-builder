#!/bin/sh

echo "Executando script de entrypoint..."

# Executa o script de criação/seeding do banco de dados
python create_db.py

echo "Script de criação/seeding do banco de dados concluído."

# NOVO: Executa o script de raspagem da Tier List e salva no banco de dados
echo "Executando scraper da Tier List..."
python app/tierlist_scraper.py
echo "Scraper da Tier List concluído."

# Inicia a aplicação principal (Gunicorn)
echo "Iniciando Gunicorn..."
exec gunicorn -b 0.0.0.0:5000 wsgi:app --log-level debug --access-logfile - --error-logfile -