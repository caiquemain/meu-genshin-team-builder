# backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
import os

# Adicionar load_all_weapons_data
from .data_loader import (
    load_all_character_data,
    load_all_artifacts_data,
    load_all_weapons_data  # <-- ADICIONADO
)
from .services.team_suggester import load_defined_compositions


def create_app():
    app = Flask(__name__)
    CORS(app)

    with app.app_context():
        print("INFO: Iniciando carregamento de dados da aplicação...")
        load_all_character_data()
        load_all_artifacts_data()
        load_all_weapons_data()  # <-- CHAMADA ADICIONADA
        load_defined_compositions()
        print("INFO: Carregamento de dados da aplicação concluído.")

    from . import routes
    app.register_blueprint(routes.bp)

    return app
