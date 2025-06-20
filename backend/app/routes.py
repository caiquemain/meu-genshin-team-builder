# backend/app/routes.py
from flask import Blueprint, jsonify, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps

from . import db
from . import csrf_protect
from flask_wtf.csrf import generate_csrf

from .models import User, OwnedCharacter, TierListEntry  # Importar TierListEntry

from .data_loader import (
    get_all_characters_list,
    get_all_characters_map,
    get_all_artifacts_list,
    get_all_weapons_list,
    get_teams_for_character_from_file
)
from .services import team_suggester

bp = Blueprint('api', __name__, url_prefix='/api')

# --- DECORADOR CUSTOMIZADO PARA AUTORIZAÇÃO POR PAPEL ---


def role_required(role):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.has_role(role):
                return jsonify({"message": f"Acesso negado. Requer papel: {role}."}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- ROTAS DE AUTENTICAÇÃO ---


@bp.route('/register', methods=['POST'])
@csrf_protect.exempt
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Usuário e senha são obrigatórios"}), 400

    if len(username) < 3 or len(username) > 20:
        return jsonify({"message": "O nome de usuário deve ter entre 3 e 20 caracteres."}), 400
    if len(password) < 8:
        return jsonify({"message": "A senha deve ter no mínimo 8 caracteres."}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Usuário já existe"}), 409

    new_user = User(username=username)  # type: ignore
    new_user.set_password(password)
    new_user.role = 'user'
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuário registrado com sucesso!"}), 201


@bp.route('/login', methods=['POST'])
@csrf_protect.exempt
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify({"message": f"Login bem-sucedido! Bem-vindo, {user.username}.", "role": user.role}), 200
    else:
        return jsonify({"message": "Credenciais inválidas"}), 401


@bp.route('/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({"message": f"Olá, {current_user.username}! Este é um conteúdo protegido. Seu ID é {current_user.id}. Seu papel é {current_user.role}."})


@bp.route('/admin-only', methods=['GET'])
@role_required('admin')
def admin_only_route():
    return jsonify({"message": f"Olá, ADMIN {current_user.username}! Você tem acesso a conteúdo exclusivo de administrador."})


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout bem-sucedido!"})


@bp.route('/csrf-token', methods=['GET'])
@login_required
def get_csrf_token():
    return jsonify({'csrf_token': generate_csrf()})

# --- ROTAS PARA GERENCIAMENTO DE PERSONAGENS POSSUÍDOS ---


@bp.route('/user/characters', methods=['GET'])
@login_required
def get_owned_characters():
    owned_char_ids = [
        oc.character_id for oc in current_user.owned_characters_association]
    return jsonify(owned_char_ids)


@bp.route('/user/characters', methods=['POST'])
@login_required
def update_owned_characters():
    data = request.get_json()
    owned_character_ids_from_request = data.get('character_ids', [])

    if not isinstance(owned_character_ids_from_request, list):
        return jsonify({"error": "A entrada deve ser uma lista de IDs de personagens."}), 400

    all_valid_character_ids = set(get_all_characters_map().keys())
    for char_id in owned_character_ids_from_request:
        if not isinstance(char_id, str) or char_id.strip() == '':
            return jsonify({"error": f"ID de personagem inválido encontrado: '{char_id}'."}), 400
        if char_id not in all_valid_character_ids:
            return jsonify({"error": f"O personagem com ID '{char_id}' não é um ID de personagem válido no jogo."}), 400

    for oc in current_user.owned_characters_association:
        db.session.delete(oc)
    db.session.commit()

    new_owned_characters = []
    for char_id in owned_character_ids_from_request:
        new_owned_char = OwnedCharacter(
            user_id=current_user.id, character_id=char_id)  # type: ignore
        db.session.add(new_owned_char)
        new_owned_characters.append(char_id)

    db.session.commit()

    return jsonify({"message": "Personagens possuídos atualizados com sucesso.", "owned_characters": new_owned_characters}), 200

# --- ROTAS DE DADOS ---


@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Backend está funcionando!"}), 200


@bp.route('/characters', methods=['GET'])
def get_characters_route():
    all_characters = get_all_characters_list()
    if not isinstance(all_characters, list):
        print("ERRO em /api/characters: Dados de personagens não carregados ou formato inválido.")
        return jsonify({"error": "Dados de personagens não disponíveis no momento."}), 500
    return jsonify(all_characters)


@bp.route('/artifacts-database', methods=['GET'])
def get_artifacts_database_route():
    all_artifacts = get_all_artifacts_list()
    if not isinstance(all_artifacts, list):
        print("ERRO em /api/artifacts-database: Dados de artefatos não carregados ou formato inválido.")
        return jsonify({"error": "Banco de dados de artefatos não disponível no momento."}), 500
    return jsonify(all_artifacts)


@bp.route('/weapons-database', methods=['GET'])
def get_weapons_database_route():
    all_weapons = get_all_weapons_list()
    if not isinstance(all_weapons, list):
        print("ERRO em /api/weapons-database: Dados de armas não carregados ou formato inválido.")
        return jsonify({"error": "Banco de dados de armas não disponível no momento."}), 500
    return jsonify(all_weapons)


@bp.route('/character/<string:character_id>', methods=['GET'])
def get_specific_character_route(character_id):
    all_chars_map = get_all_characters_map()
    character_data = all_chars_map.get(character_id)

    if not character_data:
        return jsonify({"error": f"Personagem com ID '{character_id}' não encontrado."}), 404
    return jsonify(character_data)


@bp.route('/teams-for-character/<string:character_id>', methods=['GET'])
def get_character_teams_route(character_id):
    team_templates_for_char = get_teams_for_character_from_file(character_id)
    all_chars_map_for_population = get_all_characters_map()
    populated_teams_list = []

    if not all_chars_map_for_population:
        print(
            f"ERRO: Falha ao carregar all_chars_map_for_population para popular times de {character_id}")
        return jsonify({"error": "Dados de personagens base não puderam ser carregados no servidor."}), 500

    for team_template in team_templates_for_char:
        populated_team = dict(team_template)
        populated_team["characters_in_team"] = []
        template_character_slots = team_template.get("characters_in_team", [])

        if len(template_character_slots) != 4:
            print(
                f"AVISO: Template de time '{team_template.get('name')}' para '{character_id}' não tem 4 personagens, pulando.")
            continue

        all_slots_valid = True
        for slot_info in template_character_slots:
            char_id_in_slot = slot_info.get("character_id")
            char_build_key = slot_info.get("build_key")
            base_char_data_from_map = all_chars_map_for_population.get(
                char_id_in_slot)

            if base_char_data_from_map:
                specific_build_details = None
                build_options = base_char_data_from_map.get(
                    "build_options", [])
                if char_build_key and build_options:
                    specific_build_details = next(
                        (b for b in build_options if b.get("key") == char_build_key), None)

                if not specific_build_details and build_options:
                    specific_build_details = build_options[0]
                    print(
                        f"AVISO: Build com key '{char_build_key}' não encontrada para '{char_id_in_slot}'. Usando a primeira build disponível.")
                elif not build_options:
                    print(
                        f"AVISO: Nenhuma build_options encontrada para '{char_id_in_slot}'.")

                char_slot_for_display = {
                    "id": base_char_data_from_map.get("id"),
                    "name": base_char_data_from_map.get("name"),
                    "icon_url": base_char_data_from_map.get("icon_url"),
                    "element": base_char_data_from_map.get("element"),
                    "rarity": base_char_data_from_map.get("rarity"),
                    "role_in_team": slot_info.get("role_in_team"),
                    "build_key": char_build_key,
                    "build_details": specific_build_details if specific_build_details else {}
                }
                populated_team["characters_in_team"].append(
                    char_slot_for_display)
            else:
                print(
                    f"AVISO: Personagem com ID '{char_id_in_slot}' do template de time '{team_template.get('name')}' não encontrado.")
                all_slots_valid = False
                break

        if all_slots_valid:
            populated_teams_list.append(populated_team)

    return jsonify(populated_teams_list)


@bp.route('/suggest-team', methods=['POST'])
def suggest_team_route():
    data = request.get_json()
    if not data or 'owned_characters' not in data:
        return jsonify({"error": "Dados inválidos. 'owned_characters' é esperado."}), 400

    owned_character_ids_set = set(data['owned_characters'])
    all_characters_info_list_for_suggester = get_all_characters_list()

    if not isinstance(all_characters_info_list_for_suggester, list) or not all_characters_info_list_for_suggester:
        print("ERRO em /api/suggest-team: Dados de personagens não carregados ou formato inválido para o sugestor.")
        return jsonify({"error": "Não foi possível carregar os dados dos personagens no servidor para sugestão."}), 500

    suggested_teams = team_suggester.generate_teams_from_owned(
        owned_character_ids_set, all_characters_info_list_for_suggester
    )
    return jsonify(suggested_teams)

# --- ROTA PARA OBTER A TIER LIST CONSOLIDADA ---
# Importe o modelo TierListEntry no topo do routes.py: from .models import User, OwnedCharacter, TierListEntry


@bp.route('/tierlist', methods=['GET'])
def get_tier_list_route():
    try:
        tier_list_entries = TierListEntry.query.all()
        tier_list_data = []
        for entry in tier_list_entries:
            tier_list_data.append({
                "character_id": entry.character_id,
                "character_name": entry.character_name,
                "tier_level": entry.tier_level,
                "role": entry.role,
                "constellation": entry.constellation,
                "rarity": entry.rarity,
                "element": entry.element,
                "average_numeric_tier": entry.average_numeric_tier,  # <-- ADICIONADO
                "sources_contributing": entry.sources_contributing,  # <-- ADICIONADO
                "original_scores_by_site": entry.original_scores_by_site  # <-- ADICIONADO
            })
        return jsonify(tier_list_data), 200
    except Exception as e:
        print(f"ERRO ao buscar tierlist do DB: {e}")
        return jsonify({"error": "Não foi possível carregar a Tier List no momento."}), 500
