# backend/wsgi.py
from app import create_app  # Importa a função de fábrica
app = create_app()  # Chama a função para obter a instância da aplicação Flask
