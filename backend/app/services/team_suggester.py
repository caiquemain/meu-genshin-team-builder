# backend/app/services/team_suggester.py
import json
import os
import random
import secrets
import uuid

# --- Variável Global e Função de Carregamento de COMPOSIÇÕES DE TIMES ---
DEFINED_COMPOSITIONS = []
COMPOSITIONS_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'team_data')


def load_defined_compositions():
    global DEFINED_COMPOSITIONS
    new_compositions = []
    if not os.path.exists(COMPOSITIONS_DATA_PATH):
        print(
            f"AVISO CRÍTICO: Diretório de dados de composições de times não encontrado: {COMPOSITIONS_DATA_PATH}")
        DEFINED_COMPOSITIONS = new_compositions
        return

    print(
        f"INFO: Carregando composições de times de: {COMPOSITIONS_DATA_PATH}")
    found_files = False
    for filename in os.listdir(COMPOSITIONS_DATA_PATH):
        if filename.endswith(".json"):
            found_files = True
            filepath = os.path.join(COMPOSITIONS_DATA_PATH, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        new_compositions.extend(data)
                    else:
                        print(
                            f"AVISO: Arquivo JSON {filename} em team_data/ não contém uma lista de composições.")
            except json.JSONDecodeError:
                print(
                    f"ERRO: Não foi possível decodificar JSON de {filename} em team_data/.")
            except Exception as e:
                print(
                    f"ERRO: Não foi possível carregar composições de {filename} em team_data/: {str(e)}")

    DEFINED_COMPOSITIONS = new_compositions
    if DEFINED_COMPOSITIONS:
        print(
            f"INFO: Total de {len(DEFINED_COMPOSITIONS)} templates de composições de times carregados.")
    elif found_files:
        print("AVISO: Nenhum template de composição de time válido foi carregado de team_data/, embora arquivos JSON tenham sido encontrados.")
    else:
        print(
            f"AVISO: Nenhum arquivo .json de composição de time encontrado em {COMPOSITIONS_DATA_PATH}.")


# Carrega as composições de times quando o módulo é importado
load_defined_compositions()


def _character_matches_criteria(character_obj, criteria, current_team_ids_being_built):
    # (Mantenha esta função helper como na resposta #25 - para preencher flex slots se você usar essa lógica)
    # Por agora, a lógica principal abaixo assume que `characters_in_team` no template já define os 4.
    if character_obj['id'] in current_team_ids_being_built:
        return False
    if "character_id_options" in criteria and character_obj['id'] not in criteria["character_id_options"]:
        return False
    if "element" in criteria and character_obj.get("element") != criteria["element"]:
        return False
    if "role_hint" in criteria and not any(role in character_obj.get("role", []) for role in criteria["role_hint"]):
        return False
    if criteria.get("must_be_hydro_or_dendro", False) and character_obj.get("element") not in ["Hydro", "Dendro"]:
        return False
    return True


def generate_teams_from_owned(owned_character_ids_set, all_characters_info_list):
    suggested_teams_output = []

    # Criar um mapa de todos os personagens (com suas build_options) para busca rápida por ID
    all_chars_map_with_builds = {
        char['id']: char for char in all_characters_info_list if 'id' in char}

    # Filtrar para obter os objetos completos apenas dos personagens que o usuário possui
    owned_character_objects = [all_chars_map_with_builds[char_id]
                               for char_id in owned_character_ids_set if char_id in all_chars_map_with_builds]

    if not owned_character_objects:
        return [{"error": "Nenhum personagem válido fornecido ou encontrado nos dados gerais."}]

    # 1. Tentar corresponder às composições definidas em DEFINED_COMPOSITIONS
    for comp_template in DEFINED_COMPOSITIONS:
        template_character_slots = comp_template.get("characters_in_team", [])

        if len(template_character_slots) != 4:  # Pular templates malformados ou incompletos
            # print(f"DEBUG: Template {comp_template.get('name')} pulado, não tem 4 personagens em characters_in_team.")
            continue

        team_is_formable = True
        current_team_populated_chars = []

        for slot_info_from_template in template_character_slots:
            char_id = slot_info_from_template.get("character_id")

            if not (char_id and char_id in owned_character_ids_set and char_id in all_chars_map_with_builds):
                # Personagem do template não possuído ou não encontrado nos dados gerais
                team_is_formable = False
                break

            base_char_data = all_chars_map_with_builds[char_id]
            resolved_build_details = {}  # Começa vazio

            build_key_from_template = slot_info_from_template.get("build_key")
            character_build_options = base_char_data.get("build_options", [])

            if build_key_from_template and character_build_options:
                found_build = next((b for b in character_build_options if b.get(
                    "key") == build_key_from_template), None)
                if found_build:
                    # Contém name, artifacts, weapons, etc. da build
                    resolved_build_details = found_build
                else:
                    # print(f"AVISO: Build key '{build_key_from_template}' não encontrada para {char_id} no template '{comp_template.get('name')}'. Usando primeira build se disponível.")
                    if character_build_options:  # Pega a primeira build como default se a chave não for encontrada
                        resolved_build_details = character_build_options[0]
            elif character_build_options:  # Se não há build_key no template, pega a primeira build do personagem como default
                # print(f"AVISO: Nenhuma build_key especificada para {char_id} no template '{comp_template.get('name')}'. Usando primeira build se disponível.")
                resolved_build_details = character_build_options[0]
            # else:
                # print(f"AVISO: Nenhuma build_options encontrada para {char_id} ou nenhuma build_key especificada e sem default.")
                # resolved_build_details permanecerá {} se nenhuma build for encontrada/definida

            # Aplicar build_overrides (simplificado por enquanto)
            # Para uma implementação completa, você precisaria de um merge profundo aqui.
            overrides = slot_info_from_template.get("build_overrides", {})
            if overrides:
                # Exemplo simples: se 'notes_override' existir, adiciona/substitui uma nota na build
                if "notes_override" in overrides:
                    # Adiciona se não existir
                    if not resolved_build_details.get("notes_build"):
                        resolved_build_details["notes_build"] = ""
                    resolved_build_details["notes_build"] += " (Time Específico: " + \
                        overrides["notes_override"] + ")"
                # Você pode expandir para outros campos como main_stats, weapons, etc.

            populated_char_info = {
                "id": base_char_data.get("id"),
                "name": base_char_data.get("name"),
                "icon_url": base_char_data.get("icon_url"),
                "element_icon_url": base_char_data.get("element_icon_url"),
                "element": base_char_data.get("element"),
                "rarity": base_char_data.get("rarity"),
                # Adicione outros campos base do personagem que a TeamDetailPage possa precisar
                "role_in_team": slot_info_from_template.get("role_in_team", "Função não especificada"),
                # Este agora é o objeto da build resolvido
                "build_details": resolved_build_details
            }
            current_team_populated_chars.append(populated_char_info)

        if team_is_formable and len(current_team_populated_chars) == 4:
            suggested_teams_output.append({
                # Substitua random.randint por uuid.uuid4() para gerar um ID único e seguro
                "id": comp_template.get("id", comp_template.get("name", "team_") + str(uuid.uuid4())),
                "name": comp_template.get("name", "Time Sugerido"),
                "strategy": comp_template.get("strategy", "Estratégia não definida."),
                "characters_in_team": current_team_populated_chars
            })

    # 2. Fallback: Time aleatório se nenhuma composição definida for encontrada
    if not suggested_teams_output and len(owned_character_objects) >= 4:
        random.shuffle(owned_character_objects)
        team_for_random_display = []
        for char_obj in owned_character_objects[:4]:
            default_build = {}
            if char_obj.get("build_options") and len(char_obj["build_options"]) > 0:
                # Pega a primeira build como default
                default_build = char_obj["build_options"][0]

            team_for_random_display.append({
                # Inclui todos os campos de char_obj (id, name, icon_url, build_options, etc.)
                **char_obj,
                "role_in_team": (char_obj.get("role") and char_obj["role"][0]) if char_obj.get("role") else "Flex",
                "build_details": default_build
            })

        suggested_teams_output.append({
            "id": "random_team_" + str(secrets.randbelow(9000) + 1000),
            "name": "Time Aleatório Sugerido",
            "characters_in_team": team_for_random_display,
            "strategy": "Um time gerado aleatoriamente com seus personagens. As builds mostradas são as primeiras definidas para cada um (se disponíveis)."
        })

    # 3. Mensagens de resultado
    if not suggested_teams_output:
        if 0 < len(owned_character_objects) < 4:
            # Para mensagens de erro, a estrutura anterior 'characters' é mais simples
            error_chars_display = [{"id": c.get("id"), "name": c.get(
                "name"), "icon_url": c.get("icon_url")} for c in owned_character_objects]
            return [{"error": "Personagens Insuficientes",
                     "message": f"Você selecionou {len(owned_character_objects)}. São necessários 4 para um time.",
                     "characters": error_chars_display}]
        else:
            return [{"message": "Não foi possível encontrar composições específicas ou gerar um time aleatório com os personagens selecionados."}]

    return suggested_teams_output
