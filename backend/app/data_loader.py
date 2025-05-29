# backend/app/data_loader.py
import json
import os

# --- Caminhos ---
BASE_APP_DIR = os.path.dirname(os.path.abspath(__file__))
CHARACTER_DEFINITIONS_PATH = os.path.join(
    BASE_APP_DIR, 'character_definitions')
GAME_DATA_PATH = os.path.join(BASE_APP_DIR, 'game_data')
# Caminho para a pasta team_data, assumindo que está em services/
TEAM_DATA_PATH = os.path.join(BASE_APP_DIR, 'services', 'team_data')


# --- Dados dos Personagens ---
ALL_CHARACTERS_MAP = {}
ALL_CHARACTERS_LIST = []

# --- Dados dos Artefatos ---
ALL_ARTIFACTS_MAP = {}
ALL_ARTIFACTS_LIST = []

# --- Dados das Armas ---
ALL_WEAPONS_MAP = {}
ALL_WEAPONS_LIST = []


def load_all_character_data():
    global ALL_CHARACTERS_MAP, ALL_CHARACTERS_LIST
    loaded_chars_map = {}
    loaded_chars_list = []
    if not os.path.exists(CHARACTER_DEFINITIONS_PATH):
        print(
            f"AVISO CRÍTICO: O diretório de definições de personagens não foi encontrado: {CHARACTER_DEFINITIONS_PATH}")
        ALL_CHARACTERS_MAP, ALL_CHARACTERS_LIST = {}, []
        return
    print(
        f"INFO: Carregando definições de personagens de: {CHARACTER_DEFINITIONS_PATH}")
    found_files = False
    for filename in os.listdir(CHARACTER_DEFINITIONS_PATH):
        if filename.endswith(".json"):
            found_files = True
            filepath = os.path.join(CHARACTER_DEFINITIONS_PATH, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    char_data = json.load(f)
                    if isinstance(char_data, dict) and 'id' in char_data:
                        loaded_chars_map[char_data['id']] = char_data
                        loaded_chars_list.append(char_data)
                    else:
                        print(
                            f"AVISO: Arquivo JSON {filename} em character_definitions/ não contém um objeto de personagem válido com 'id'.")
            except Exception as e:
                print(
                    f"ERRO ao carregar dados do personagem de {filename}: {str(e)}")
    ALL_CHARACTERS_MAP, ALL_CHARACTERS_LIST = loaded_chars_map, loaded_chars_list
    if found_files and ALL_CHARACTERS_LIST:
        print(
            f"INFO: Total de {len(ALL_CHARACTERS_LIST)} definições de personagens carregadas.")
    elif found_files:
        print(
            f"AVISO: Arquivos JSON de personagem encontrados em {CHARACTER_DEFINITIONS_PATH}, mas nenhum dado válido foi carregado.")
    else:
        print(
            f"AVISO: Nenhum arquivo .json de personagem encontrado em {CHARACTER_DEFINITIONS_PATH}.")


def get_all_characters_list():
    return ALL_CHARACTERS_LIST


def get_all_characters_map():
    return ALL_CHARACTERS_MAP


def load_all_artifacts_data():
    global ALL_ARTIFACTS_MAP, ALL_ARTIFACTS_LIST
    loaded_artifacts_map = {}
    loaded_artifacts_list = []
    artifacts_file_path = os.path.join(
        GAME_DATA_PATH, 'artifacts_database.json')

    if not os.path.exists(artifacts_file_path):
        print(
            f"AVISO CRÍTICO: Arquivo artifacts_database.json não encontrado em: {artifacts_file_path}")
        ALL_ARTIFACTS_MAP, ALL_ARTIFACTS_LIST = {}, []
        return

    print(
        f"INFO: Carregando banco de dados de artefatos de: {artifacts_file_path}")
    try:
        with open(artifacts_file_path, 'r', encoding='utf-8') as f:
            artifacts_data = json.load(f)
            if isinstance(artifacts_data, list):
                for artifact_set in artifacts_data:
                    if isinstance(artifact_set, dict) and 'id' in artifact_set:
                        loaded_artifacts_map[artifact_set['id']] = artifact_set
                        loaded_artifacts_list.append(artifact_set)
                    else:
                        print(
                            f"AVISO: Item inválido encontrado em artifacts_database.json (sem 'id' ou não é um dicionário).")
            else:
                print(
                    f"AVISO: artifacts_database.json não contém uma lista de artefatos no formato esperado.")
    except Exception as e:
        print(f"ERRO ao carregar artifacts_database.json: {str(e)}")

    ALL_ARTIFACTS_MAP, ALL_ARTIFACTS_LIST = loaded_artifacts_map, loaded_artifacts_list
    if ALL_ARTIFACTS_LIST:
        print(
            f"INFO: Total de {len(ALL_ARTIFACTS_LIST)} conjuntos de artefatos carregados.")
    else:
        print("AVISO: Nenhum conjunto de artefatos válido foi carregado.")


def get_all_artifacts_list():
    return ALL_ARTIFACTS_LIST


def get_artifact_by_id(artifact_id):
    return ALL_ARTIFACTS_MAP.get(artifact_id)


def load_all_weapons_data():
    global ALL_WEAPONS_MAP, ALL_WEAPONS_LIST
    loaded_weapons_map = {}
    loaded_weapons_list = []
    weapons_file_path = os.path.join(GAME_DATA_PATH, 'weapons_database.json')

    if not os.path.exists(weapons_file_path):
        print(
            f"AVISO CRÍTICO: Arquivo weapons_database.json não encontrado em: {weapons_file_path}")
        ALL_WEAPONS_MAP, ALL_WEAPONS_LIST = {}, []
        return

    print(f"INFO: Carregando banco de dados de armas de: {weapons_file_path}")
    try:
        with open(weapons_file_path, 'r', encoding='utf-8') as f:
            weapons_data = json.load(f)
            if isinstance(weapons_data, list):
                for weapon in weapons_data:
                    if isinstance(weapon, dict) and 'id' in weapon:
                        loaded_weapons_map[weapon['id']] = weapon
                        loaded_weapons_list.append(weapon)
                    else:
                        print(
                            f"AVISO: Item inválido encontrado em weapons_database.json (sem 'id' ou não é um dicionário).")
            else:
                print(
                    f"AVISO: weapons_database.json não contém uma lista de armas no formato esperado.")
    except Exception as e:
        print(f"ERRO ao carregar weapons_database.json: {str(e)}")

    ALL_WEAPONS_MAP, ALL_WEAPONS_LIST = loaded_weapons_map, loaded_weapons_list
    if ALL_WEAPONS_LIST:
        print(f"INFO: Total de {len(ALL_WEAPONS_LIST)} armas carregadas.")
    else:
        print("AVISO: Nenhuma arma válida foi carregada de weapons_database.json.")


def get_all_weapons_list():
    return ALL_WEAPONS_LIST


def get_weapon_by_id(weapon_id):
    return ALL_WEAPONS_MAP.get(weapon_id)

# --- FUNÇÃO PARA CARREGAR TIMES DE UM PERSONAGEM ESPECÍFICO (TEAM_DATA) ---


def get_teams_for_character_from_file(character_id):
    """
    Carrega e retorna os templates de composição de time para um personagem específico
    do arquivo team_data/character_id.json.
    """
    team_templates = []
    # Sanitiza o character_id para formar um nome de arquivo seguro
    safe_character_id = "".join(
        c for c in character_id if c.isalnum() or c in ('_', '-')).lower()
    team_file_path = os.path.join(TEAM_DATA_PATH, f"{safe_character_id}.json")

    if not os.path.exists(team_file_path):
        print(
            f"INFO: Arquivo de times para '{character_id}' (esperado como '{safe_character_id}.json') não encontrado em: {team_file_path}. Retornando lista vazia.")
        return team_templates

    try:
        with open(team_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                team_templates = data
                # print(f"INFO: Carregados {len(team_templates)} templates de time para {character_id} de {team_file_path}")
            else:
                print(
                    f"AVISO: Arquivo JSON {safe_character_id}.json em team_data/ não contém uma lista de composições no formato esperado.")
    except json.JSONDecodeError:
        print(
            f"ERRO: Não foi possível decodificar JSON de {safe_character_id}.json em team_data/.")
    except Exception as e:
        print(
            f"ERRO: Não foi possível carregar composições de {safe_character_id}.json em team_data/: {str(e)}")

    return team_templates
