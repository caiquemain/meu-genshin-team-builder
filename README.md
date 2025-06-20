# Genshin Impact - Assistente de Times e Builds

Bem-vindo ao Genshin Impact - Assistente de Times e Builds! Este projeto é uma ferramenta web desenvolvida para ajudar jogadores de Genshin Impact a descobrir informações detalhadas sobre personagens, suas builds recomendadas e sugestões de composições de time.

![Badge - Projeto em Desenvolvimento](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Badge - React](https://img.shields.io/badge/Frontend-React-blue?logo=react)
![Badge - Flask](https://img.shields.io/badge/Backend-Flask-green?logo=flask)
![Badge - Docker](https://img.shields.io/badge/Containerization-Docker-blue?logo=docker)


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
* **Tier List Consolidada (NOVO!):**
    * Uma Tier List dinâmica que agrega e calcula uma média de pontuações de personagens de múltiplos sites externos (genshin.gg, game8.co, genshinlab.com).
    * Visualização clara por tiers (SS, S, A, B, C, D) com cores distintivas.
    * Cards de personagem com ícones de elemento e um efeito visual de hover baseado na raridade (dourado para 5\*, roxo para 4\*).
    * **Tooltip interativa** ao passar o mouse sobre o personagem, exibindo:
        * Função (role), Elemento e Raridade.
        * **Nota agregada** (calculada pela média das fontes) com a cor correspondente ao seu tier.
        * Pontuações individuais e tiers de cada site que contribuiu para a consolidação.

## 🛠️ Tecnologias Utilizadas

* **Frontend:**
    * React (com Vite)
    * JavaScript (JSX)
    * CSS (com variáveis CSS para temas)
    * Axios (para chamadas API)
    * React Router (para navegação)
* **Backend:**
    * Python (Flask)
    * Flask-SQLAlchemy (ORM para banco de dados)
    * SQLite (Banco de dados de desenvolvimento/local)
    * BeautifulSoup4 (para raspagem de dados)
    * Selenium (para raspagem de sites dinâmicos)
    * Gunicorn (servidor WSGI para produção)
    * Flask-CORS (para gerenciar requisições cross-origin)
    * Flask-Login (para gerenciamento de usuários)
    * Flask-WTF (para proteção CSRF)
* **Infraestrutura/Containerização:**
    * Docker
    * Docker Compose (para orquestração de múltiplos serviços)
    * Nginx (como proxy reverso no contêiner frontend)
* **Dados:**
    * Arquivos JSON (`backend/app/character_definitions/`, `backend/app/game_data/`, `backend/app/services/team_data/`).
    * Dados raspados de Tier Lists externas (`scraped_tier_lists/`).

## 📂 Estrutura do Projeto

O projeto é organizado da seguinte forma:

-   `backend/`                    # Aplicação Flask (Python)
    -   `app/`                    # Núcleo da aplicação Flask
        -   `character_definitions/` # Arquivos JSON com dados detalhados dos personagens (inclui Skirk, Dahlia, etc.)
        -   `game_data/`          # JSONs de artefatos e armas (inclui Finale of the Deep)
        -   `scrapers/`           # Módulos para raspagem de dados de sites externos (genshin.gg, game8.co, genshinlab.com)
        -   `services/`           # Lógica de serviços (ex: sugestão de times)
            -   `team_data/`      # Arquivos JSON com templates de times
        -   `data_loader.py`      # Carrega dados dos JSONs para memória
        -   `models.py`           # Modelos de dados do SQLAlchemy (inclui `TierListEntry` com dados consolidados)
        -   `routes.py`           # Definições das rotas da API (inclui `/api/tierlist`)
        -   `tierlist_orchestrator.py` # Script para raspar, consolidar e popular o DB da Tier List
        -   `__init__.py`         # Inicialização da aplicação Flask e extensões
    -   `config.py`               # Configurações do Flask
    -   `requirements.txt`        # Dependências Python
    -   `run.py`                  # Ponto de entrada para rodar o backend Flask
-   `frontend/`                   # Aplicação React (Vite)
    -   `public/`                 # Arquivos públicos e assets (imagens: personagens, elementos, raridade, etc.)
        -   `assets/`
            -   `images/`
                -   `characters/` # Imagens de personagens (inclui Skirk, Dahlia)
                -   `elements/`   # Ícones de elementos
                -   `rarity/`     # Ícones de raridade (se usados)
                -   `weapons_detail/` # Imagens de armas (inclui Finale of the Deep)
    -   `src/`                    # Código fonte do frontend
        -   `components/`         # Componentes React reutilizáveis (CharacterTooltip, etc.)
        -   `contexts/`           # Contextos React (Tema, SelectedCharacters)
        -   `pages/`              # Componentes de página (TierListPage, TeamBuilderPage, CharacterProfilePage, LoginPage)
        -   `services/`           # Serviços (ex: chamadas API: `tierListService.js`)
        -   `App.jsx`             # Componente principal da aplicação (define rotas)
        -   `main.jsx`            # Ponto de entrada do React (renderiza App, envolve com Providers)
        -   `App.css`             # Estilos globais da aplicação (controle de tema claro/escuro)
        -   `index.css`           # Estilos CSS de base
    -   `index.html`              # HTML principal do frontend
    -   `package.json`            # Dependências e scripts do Node.js
    -   `vite.config.js`          # Configuração do Vite
    -   `nginx.conf`              # Configuração do Nginx para proxy reverso (se usado no frontend)
-   `docker-compose.yml`          # Configuração dos serviços Docker e orquestração
-   `.gitignore`                  # Arquivos e pastas a serem ignorados pelo Git
-   `README.md`                   # Este arquivo!
-   `organizaoimagens.ps1`        # Script PowerShell para organização de imagens (se existir e for relevante)

## 🚀 Como Rodar o Projeto (Usando Docker Compose)

Para rodar este projeto localmente utilizando Docker Compose (método recomendado), siga os passos abaixo:

### Pré-requisitos

* Docker Desktop instalado (inclui Docker Engine e Docker Compose).

### Passos de Inicialização

1.  **Navegue até a raiz do projeto:**
    Abra seu terminal (CMD, PowerShell, Git Bash) e navegue até o diretório `meu-genshin-team-builder`.

2.  **Construa as imagens Docker:**
    Este comando irá construir as imagens Docker para o backend (Python/Flask) e o frontend (Node.js/React) com base nos Dockerfiles e dependências definidas. Pode levar alguns minutos na primeira vez.
    ```bash
    docker-compose build
    ```
    *Se você tiver problemas de cache ou precisar de uma reconstrução limpa, adicione `--no-cache` ao comando: `docker-compose build --no-cache`.*

3.  **Inicie os serviços Docker:**
    Este comando iniciará os contêineres do `backend` (servidor Flask) e do `frontend` (servidor Nginx/Vite para o React) em segundo plano.
    ```bash
    docker-compose up -d
    ```

4.  **Popule o Banco de Dados com Dados Consolidados (Tier List):**
    Após os serviços estarem rodando, execute o orquestrador. Este script irá raspar dados de Tier Lists externas, consolidá-los e salvá-los no banco de dados SQLite do backend. **Este passo é essencial para que a página de Tier List funcione.**
    ```bash
    docker-compose exec backend python -m app.tierlist_orchestrator
    ```
    *Acompanhe os logs deste comando. Você verá o progresso da raspagem e da consolidação. Se houver erros como 'AttributeError' ou 'OperationalError' relacionados ao DB, você pode precisar limpar o volume do Docker (`docker-compose down --volumes`) e rodar o orquestrador novamente.*

5.  **Acesse a Aplicação:**
    Abra seu navegador e acesse:
    * **Página Principal (Team Builder):** `http://localhost:3000/`
    * **Página da Tier List:** `http://localhost:3000/tierlist`

## 🐳 Comandos Docker Úteis

* `docker-compose ps`               : Lista os contêineres em execução.
* `docker-compose logs [service_name]` : Exibe os logs de um serviço (ex: `docker-compose logs backend`).
* `docker-compose down`             : Para e remove os contêineres e redes.
* `docker-compose down --volumes`   : Para e remove contêineres, redes E volumes (útil para limpar o banco de dados de desenvolvimento).
* `docker-compose exec [service_name] [command]` : Executa um comando dentro de um contêiner em execução (ex: `docker-compose exec backend bash` para entrar no shell).

## 🤝 Como Contribuir

Contribuições são bem-vindas! Se você tem ideias para novas funcionalidades, melhorias na interface, correções de bugs, ou quer adicionar/atualizar dados de personagens e builds, sinta-se à vontade para:

1.  Fazer um Fork do projeto.
2.  Criar uma nova Branch (`git checkout -b feature/NovaFuncionalidade`).
3.  Realizar suas alterações.
4.  Fazer o Commit (`git commit -m 'feat(nova-funcionalidade): Adiciona Nova Funcionalidade'`).
5.  Enviar para a Branch (`git push origin feature/NovaFuncionalidade`).
6.  Abrir um Pull Request.

### Adicionando/Atualizando Dados

* **Informações de Personagens:** Edite os arquivos JSON correspondentes em `backend/app/character_definitions/` (inclua novas imagens em `frontend/public/assets/images/characters/`).
* **Informações de Times:** Edite ou adicione arquivos JSON em `backend/app/services/team_data/`.
* **Informações de Artefatos/Armas:** Atualize os arquivos em `backend/app/game_data/` (inclua novas imagens em `frontend/public/assets/images/artifact_sets/` ou `frontend/public/assets/images/weapons_detail/`).
* Certifique-se de manter a estrutura JSON existente.
* Após adicionar ou atualizar dados de personagem, artefato ou arma, **lembre-se de rodar o orquestrador** (`docker-compose exec backend python -m app.tierlist_orchestrator`) para que a Tier List seja atualizada no banco de dados.

## 📜 Referências e Fontes de Dados

As informações de personagens, builds e times são compiladas a partir de diversas fontes da comunidade Genshin Impact, incluindo (mas não se limitando a):

* Genshin Impact Wiki (Fandom)
* KeqingMains (KQM)
* Genshin.gg (para dados da Tier List)
* Game8.co (para dados da Tier List)
* Genshinlab.com (para dados da Tier List)
* Outras comunidades e guias de jogadores experientes.

Nosso objetivo é fornecer dados precisos e úteis. As fontes específicas utilizadas para cada personagem e suas builds são listadas na seção "Referências" dentro da página de perfil de cada personagem.


Feito com ❤️ para a comunidade Genshin Impact!