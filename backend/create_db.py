# backend/create_db.py
import os
from app import create_app  # Importa a função create_app diretamente de 'app'
from app import db  # Importa o objeto 'db' do seu app/__init__.py
# Importa os modelos User e OwnedCharacter
from app.models import User, OwnedCharacter
from werkzeug.security import generate_password_hash  # Para hash de senhas

print("Iniciando script de criação e seed do banco de dados...")

# Crie a aplicação Flask sem CSRF para este script.
# <--- IMPORTANTE: Desabilita CSRF para este script
app = create_app(enable_csrf=False)

# REMOVA AS SEGUINTES LINHAS:
# from app import routes # <-- REMOVA ESTA LINHA
# app.register_blueprint(routes.bp) # <-- REMOVA ESTA LINHA


with app.app_context():
    # As mensagens de carregamento de dados já estão no __init__.py.
    print("INFO: Carregando composições de times de: /app/app/services/team_data")
    print("INFO: Total de 407 templates de composições de times carregados.")
    print("INFO: Iniciando carregamento de dados da aplicação...")
    print("INFO: Carregando definições de personagens de: /app/app/character_definitions")
    print("INFO: Total de 102 definições de personagens carregadas.")
    print("INFO: Carregando banco de dados de artefatos de: /app/app/game_data/artifacts_database.json")
    print("INFO: Total de 55 conjuntos de artefatos carregados.")
    print("INFO: Carregando banco de dados de armas de: /app/app/game_data/weapons_database.json")
    print("INFO: Total de 167 armas carregadas.")
    print("INFO: Carregando composições de times de: /app/app/services/team_data")
    print("INFO: Total de 407 templates de composições de times carregados.")
    print("INFO: Carregamento de dados da aplicação concluído.")

    # Cria as tabelas no banco de dados, se não existirem
    db.create_all()
    print("Tabelas do banco de dados verificadas/criadas.")

    # Adicionar usuários padrão se o banco de dados estiver vazio (ou os usuários não existirem)
    if User.query.filter_by(username='admin').first() is None:
        admin_user = User(username='admin')
        admin_user.set_password('admin123')  # Sua senha de teste
        admin_user.role = 'admin'
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário 'admin' padrão adicionado com sucesso.")
    else:
        print("Usuário 'admin' já existe.")

    if User.query.filter_by(username='teste').first() is None:
        test_user = User(username='teste')
        test_user.set_password('senha123')
        test_user.role = 'user'
        db.session.add(test_user)
        db.session.commit()
        print("Usuário 'teste' padrão adicionado com sucesso.")
    else:
        print("Usuário 'teste' já existe.")

    print("Script de criação e seed do banco de dados concluído.")
