# backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_talisman import Talisman  # Manter importado se for usar Talisman
import os

# <-- Importe CSRFProtect para proteção CSRF
from flask_wtf.csrf import CSRFProtect

# Importar as funções de carregamento de dados no nível superior do módulo
from .data_loader import (
    load_all_character_data,
    load_all_artifacts_data,
    load_all_weapons_data
)
# <-- Esta função está em services/team_suggester
from .services.team_suggester import load_defined_compositions


# Crie os objetos das extensões fora da função para que possam ser importados
db = SQLAlchemy()
login_manager = LoginManager()
csrf_protect = None  # Inicialmente None, será atribuído em create_app


def create_app(enable_csrf=True):
    global csrf_protect
    app = Flask(__name__)

    # --- Configurações da Aplicação e Segurança ---
    app.config['SECRET_KEY'] = os.getenv(
        'SECRET_KEY', 'sua_chave_secreta_padrao_para_desenvolvimento_MUITO_SEGURA')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/data/site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['WTF_CSRF_ENABLED'] = True

    login_manager.session_protection = "strong"
    login_manager.login_view = 'api.login'  # type: ignore

    # --- Inicialização das Extensões ---
    db.init_app(app)
    login_manager.init_app(app)

    if enable_csrf:
        csrf_protect = CSRFProtect(app)
    else:
        class DummyCSRFProtect:
            def exempt(self, f): return f
            def protect(self, f): return f
            def generate_csrf(self): return "dummy-csrf-token"
        csrf_protect = DummyCSRFProtect()

    CORS(app,
         resources={r"/*": {"origins": "http://localhost:3000"}},
         supports_credentials=True,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-CSRFToken"]
         )

    # Talisman(app, force_https=False if app.debug else True, content_security_policy=None)

    with app.app_context():
        print("INFO: Iniciando carregamento de dados da aplicação...")
        load_all_character_data()
        load_all_artifacts_data()
        load_all_weapons_data()
        load_defined_compositions()  # Chamada correta aqui
        print("INFO: Carregamento de dados da aplicação concluído.")

        from .models import User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    from . import routes
    app.register_blueprint(routes.bp)

    return app
