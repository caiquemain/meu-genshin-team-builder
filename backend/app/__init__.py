# backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_talisman import Talisman  # Manter importado se for usar Talisman
import os
import logging

# Importe CSRFProtect para proteção CSRF
from flask_wtf.csrf import CSRFProtect

# Importar as funções de carregamento de dados no nível superior do módulo
from .data_loader import (
    load_all_character_data,
    load_all_artifacts_data,
    load_all_weapons_data
)
from .services.team_suggester import load_defined_compositions

# Crie os objetos das extensões fora da função para que possam ser importados
# por outros módulos (como models.py ou routes.py)
db = SQLAlchemy()
login_manager = LoginManager()
csrf_protect = None  # Inicialmente None, será atribuído em create_app


def create_app(enable_csrf=True):  # Adicione enable_csrf=True como argumento
    global csrf_protect  # Declare para modificar a variável global

    app = Flask(__name__)
    
    # --- Configuração de Logging para a Aplicação Flask ---
    # Defina o nível de log para a aplicação Flask.
    # DEBUG: Mais detalhado (para desenvolvimento).
    # INFO: Informações gerais (bom para produção).
    # WARNING: Avisos importantes.
    # ERROR: Erros que impedem a operação normal.
    # CRITICAL: Erros graves.
    if app.debug: # Se estiver em modo debug, logue mais detalhes
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)

    # --- Configurações da Aplicação e Segurança ---
    # Defina sua SECRET_KEY. Use variáveis de ambiente em produção para segurança!
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY', 'sua_chave_secreta_padrao_para_desenvolvimento_MUITO_SEGURA')

    # Configura o caminho do arquivo SQLite no contêiner
    # Usamos um volume no docker-compose.yml para que o arquivo .db seja persistente.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/data/site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuração para Flask-WTF CSRFProtect.
    # 'WTF_CSRF_ENABLED' deve ser True para que funcione.
    app.config['WTF_CSRF_ENABLED'] = True

    # Configuração para proteção de sessão do Flask-Login.
    login_manager.session_protection = "strong"
    # Nome da rota de login no blueprint 'api'.
    login_manager.login_view = 'api.login'

    # --- NOVAS CONFIGURAÇÕES DE LIMITES DE RECURSOS ---
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB
    app.config['MAX_FORM_MEMORY_SIZE'] = 1 * 1024 * 1024  # 1 MB
    app.config['MAX_FORM_PARTS'] = 1000  # 1000 partes

    # --- Inicialização das Extensões ---
    db.init_app(app)
    login_manager.init_app(app)

    if enable_csrf:  # Inicialize o CSRF apenas se enable_csrf for True
        csrf_protect = CSRFProtect(app)  # Inicialize CSRFProtect
    else:  # Se CSRF estiver desabilitado (modo de script como create_db.py)
        # Crie um "dummy" CSRFProtect para que os decorators em routes.py não falhem
        # ao serem avaliados durante a importação.
        class DummyCSRFProtect:
            def exempt(self, f):
                return f  # Retorna a função sem modificação

            def protect(self, f):
                return f  # Retorna a função sem modificação

            def generate_csrf(self):
                # Retorna um token dummy se a função generate_csrf for chamada
                return "dummy-csrf-token"

        csrf_protect = DummyCSRFProtect()  # Atribui o objeto dummy

    # Configurar CORS.
    CORS(app,
         # Seu frontend em desenvolvimento.
         resources={r"/*": {"origins": "http://localhost:3000"}},
         # Essencial para cookies de sessão e CSRF.
         supports_credentials=True,
         # Métodos HTTP permitidos.
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         # Cabeçalhos permitidos, incluindo o token CSRF.
         allow_headers=["Content-Type", "Authorization", "X-CSRFToken"]
         )

    # Configurar Talisman para cabeçalhos de segurança HTTP (HTTPS, CSP, etc.).
    # Descomente e configure se quiser usar Talisman.
    # Talisman(app, force_https=False if app.debug else True, content_security_policy=None)

    with app.app_context():
        print("INFO: Iniciando carregamento de dados da aplicação...")
        load_all_character_data()
        load_all_artifacts_data()
        load_all_weapons_data()
        load_defined_compositions()
        print("INFO: Carregamento de dados da aplicação concluído.")

        from .models import User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    # IMPORTANTE: Mova a importação e o registro do Blueprint de 'routes' para AQUI.
    # Isso garante que 'csrf_protect' já esteja definido (como objeto real ou dummy)
    # antes que 'routes.py' seja importado e seus decorators sejam avaliados.
    from . import routes
    app.register_blueprint(routes.bp)

    return app
