# backend/app/routes.py
from flask import Blueprint, jsonify, request
import json  # Pode ser necessário para outras partes, mas não diretamente para as novas rotas se data_loader lida com JSON

# Importar as funções necessárias do data_loader
from .data_loader import (
    get_all_characters_list,
    get_all_characters_map,  # Usaremos para buscar um personagem específico por ID
    get_all_artifacts_list,
    get_all_weapons_list,
    # Nova função para buscar times de um personagem
    get_teams_for_character_from_file
)
from .services import team_suggester  # Para a rota /suggest-team

bp = Blueprint('api', __name__, url_prefix='/api')


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


# --- NOVA ROTA PARA DADOS DE UM PERSONAGEM ESPECÍFICO ---
@bp.route('/character/<string:character_id>', methods=['GET'])
def get_specific_character_route(character_id):
    all_chars_map = get_all_characters_map()
    character_data = all_chars_map.get(character_id)

    if not character_data:
        return jsonify({"error": f"Personagem com ID '{character_id}' não encontrado."}), 404
    # Retorna o objeto completo do personagem, incluindo build_options
    return jsonify(character_data)


# --- NOVA ROTA PARA TIMES DE UM PERSONAGEM ESPECÍFICO ---
@bp.route('/teams-for-character/<string:character_id>', methods=['GET'])
def get_character_teams_route(character_id):
    team_templates_for_char = get_teams_for_character_from_file(character_id)
    # Carrega todos os dados de personagens
    all_chars_map_for_population = get_all_characters_map()
    populated_teams_list = []

    if not all_chars_map_for_population:
        print(
            f"ERRO: Falha ao carregar all_chars_map_for_population para popular times de {character_id}")
        return jsonify({"error": "Dados de personagens base não puderam ser carregados no servidor."}), 500

    for team_template in team_templates_for_char:
        populated_team = dict(team_template)  # Copia o template do time
        populated_team["characters_in_team"] = []
        template_character_slots = team_template.get("characters_in_team", [])

        if len(template_character_slots) != 4:
            print(
                f"AVISO: Template de time '{team_template.get('name')}' para '{character_id}' não tem 4 personagens, pulando.")
            continue

        all_slots_valid = True
        for slot_info in template_character_slots:
            char_id_in_slot = slot_info.get("character_id")
            # A build específica para este personagem neste time
            char_build_key = slot_info.get("build_key")
            base_char_data_from_map = all_chars_map_for_population.get(
                char_id_in_slot)

            if base_char_data_from_map:
                # Encontrar a build específica dentro de build_options do personagem
                specific_build_details = None
                build_options = base_char_data_from_map.get(
                    "build_options", [])
                if char_build_key and build_options:
                    # Procura a build pela 'key'
                    specific_build_details = next(
                        (b for b in build_options if b.get("key") == char_build_key), None)

                # Fallback se a key não for encontrada, pega a primeira build
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
                    # Adiciona os detalhes da build
                    "build_details": specific_build_details if specific_build_details else {}
                }
                populated_team["characters_in_team"].append(
                    char_slot_for_display)
            else:
                print(
                    f"AVISO: Personagem com ID '{char_id_in_slot}' do template de time '{team_template.get('name')}' não encontrado.")
                # Você pode optar por pular o time inteiro se um personagem não for encontrado
                all_slots_valid = False
                break  # Quebra o loop dos slots deste time

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

    # A função generate_teams_from_owned já lida com a lista de personagens,
    # e o team_suggester carrega suas próprias DEFINED_COMPOSITIONS (que são os templates de time).
    # A correção crítica é que generate_teams_from_owned precisa resolver as build_keys usando all_characters_info_list_for_suggester.
    suggested_teams = team_suggester.generate_teams_from_owned(
        owned_character_ids_set, all_characters_info_list_for_suggester
    )
    return jsonify(suggested_teams)
