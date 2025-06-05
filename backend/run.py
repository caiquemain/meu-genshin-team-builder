# backend/run.py
from app import create_app  # Importa a função de fábrica create_app

# Cria a instância da aplicação Flask.
# Esta variável 'app' será usada pelo comando 'flask run' se você o executar diretamente.
# Para Gunicorn, estamos usando o 'wsgi.py' como ponto de entrada.
app = create_app()

if __name__ == '__main__':
    # Quando o script é executado diretamente (ex: python run.py),
    # o servidor de desenvolvimento do Flask é iniciado.
    app.run(debug=True, port=5000)  # debug=True para desenvolvimento
