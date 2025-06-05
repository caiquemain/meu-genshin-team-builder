# Genshin Impact - Assistente de Times e Builds

Bem-vindo ao Genshin Impact - Assistente de Times e Builds! Este projeto é uma ferramenta web desenvolvida para ajudar jogadores de Genshin Impact a descobrir informações detalhadas sobre personagens, suas builds recomendadas e sugestões de composições de time.

![Badge Exemplo - Projeto em Desenvolvimento](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Badge Exemplo - React](https://img.shields.io/badge/Frontend-React-blue?logo=react)
![Badge Exemplo - Flask](https://img.shields.io/badge/Backend-Flask-green?logo=flask)

## ✨ Funcionalidades Principais

* **Perfis Detalhados de Personagens:**
    * Informações gerais: título, elemento, raridade, arma, papel na equipe, biografia, aniversário, constelação, região, afiliação e prato especial.
    * Opções de build recomendadas, incluindo artefatos, status principais/secundários e armas.
    * Detalhes sobre talentos (ataque normal, habilidade elemental, supremo) e passivas.
    * Lista de constelações com descrições.
    * Materiais de ascensão e de talento.
    * Links externos para guias e wikis (ex: KQM, Fandom Wiki).
    * Referências das fontes de informação utilizadas.
* **Sugestão de Times:**
    * Receba sugestões de times baseados nos personagens que você possui.
    * Veja times pré-definidos e recomendados para personagens específicos.
* **Banco de Dados de Artefatos e Armas:**
    * Informações sobre diversos conjuntos de artefatos e armas disponíveis no jogo.
* **Interface Amigável:**
    * Navegação intuitiva com um menu de acesso rápido nas páginas de perfil.
    * Design responsivo (assumindo que está sendo trabalhado).
    * Alternador de tema (claro/escuro).

## 🛠️ Tecnologias Utilizadas

* **Frontend:**
    * React (com Vite) 
    * JavaScript (JSX) 
    * CSS 
    * Axios (para chamadas API) 
    * React Router (para navegação) 
* **Backend:**
    * Python 
    * Flask 
* **Dados:**
    * Arquivos JSON para armazenar informações de personagens, artefatos, armas e times.

## 📂 Estrutura do Projeto

O projeto é organizado da seguinte forma:

- `backend/`                # Aplicação Flask (Python)
    - `app/`                # Núcleo da aplicação Flask
        - `character_definitions/`  # Arquivos JSON com dados dos personagens
        - `game_data/`          # JSONs de artefatos e armas
        - `services/`           # Lógica de serviços (ex: sugestão de times)
        - `team_data/`          # Arquivos JSON com dados de times
        - `data_loader.py`    # Carrega dados dos JSONs
        - `models.py`         # Modelos de dados (se houver)
        - `routes.py`         # Definições das rotas da API
    - `config.py`           # Configurações do Flask
    - `requirements.txt`    # Dependências Python
    - `run.py`              # Ponto de entrada para rodar o backend
- `frontend/`               # Aplicação React (Vite)
    - `public/`             # Arquivos públicos e assets (imagens)
    - `src/`                # Código fonte do frontend
        - `assets/`           # Assets específicos do src
        - `components/`       # Componentes React reutilizáveis
        - `contexts/`         # Contextos React (ex: Tema)
        - `pages/`            # Componentes de página (ex: CharacterProfilePage)
        - `services/`         # Serviços (ex: chamadas API)
        - `App.jsx`           # Componente principal da aplicação
        - `main.jsx`          # Ponto de entrada do React
        - `index.css`         # Estilos globais
    - `index.html`          # HTML principal do frontend
    - `package.json`        # Dependências e scripts do Node.js
    - `vite.config.js`      # Configuração do Vite
- `.gitignore`
- `README.md`               # Este arquivo!
- `organizaoimagens.ps1`    # Script PowerShell para organização de imagens
## 🚀 Como Rodar o Projeto

Para rodar este projeto localmente, siga os passos abaixo:

### Pré-requisitos

* Node.js e npm (ou Yarn) instalados
* Python 3.x e pip instalados

### Backend

1.  Navegue até a pasta `backend`:
    ```bash
    cd backend
    ```
2.  Crie e ative um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
3.  Instale as dependências Python:
    ```bash
    pip install -r requirements.txt
    ```
4.  Inicie o servidor Flask:
    ```bash
    flask run
    # Ou python run.py (dependendo de como seu run.py está configurado)
    ```
    Por padrão, o backend deverá rodar em `http://127.0.0.1:5000`.

### Frontend

1.  Em um novo terminal, navegue até a pasta `frontend`:
    ```bash
    cd frontend
    ```
2.  Instale as dependências Node.js:
    ```bash
    npm install
    # ou yarn install
    ```
3.  Inicie o servidor de desenvolvimento Vite:
    ```bash
    npm run dev
    # ou yarn dev
    ```
    Por padrão, o frontend deverá rodar em `http://localhost:5173` (ou outra porta indicada pelo Vite) e se conectará ao backend.

## 🤝 Como Contribuir

Contribuições são bem-vindas! Se você tem ideias para novas funcionalidades, melhorias na interface, correções de bugs, ou quer adicionar/atualizar dados de personagens e builds, sinta-se à vontade para:

1.  Fazer um Fork do projeto.
2.  Criar uma nova Branch (`git checkout -b feature/NovaFuncionalidade`).
3.  Realizar suas alterações.
4.  Fazer o Commit (`git commit -m 'Adiciona NovaFuncionalidade'`).
5.  Enviar para a Branch (`git push origin feature/NovaFuncionalidade`).
6.  Abrir um Pull Request.

### Adicionando/Atualizando Dados

* **Informações de Personagens:** Edite os arquivos JSON correspondentes em `backend/app/character_definitions/`.
* **Informações de Times:** Edite ou adicione arquivos JSON em `backend/app/team_data/`.
* **Informações de Artefatos/Armas:** Atualize os arquivos em `backend/app/game_data/`.
    Certifique-se de manter a estrutura JSON existente.

## 📜 Referências e Fontes de Dados

As informações de personagens, builds e times são compiladas a partir de diversas fontes da comunidade Genshin Impact, incluindo (mas não se limitando a):

* Genshin Impact Wiki (Fandom)
* KeqingMains (KQM)
* Outras comunidades e guias de jogadores experientes.

Nosso objetivo é fornecer dados precisos e úteis. As fontes específicas utilizadas para cada personagem e suas builds são (ou serão) listadas na seção "Referências" dentro da página de perfil de cada personagem.


Feito com ❤️ para a comunidade Genshin Impact!