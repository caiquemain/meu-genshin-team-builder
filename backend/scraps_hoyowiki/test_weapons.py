import os
import json
import re

# --- CONFIGURAÇÃO ---

# 1. Altere para o nome da pasta onde seus arquivos JSON estão.
#    Exemplo: 'output/weapons'
TARGET_DIRECTORY = 'weapons_data'

# 2. Lista de idiomas que todos os campos de tradução devem ter.
#    (Baseado no seu código anterior)
SUPPORTED_LANGUAGES = {
    "pt-pt", "en-us", "ja-jp", "zh-cn", "ko-kr", "ru-ru",
    "de-de", "fr-fr", "es-es", "id-id", "th-th", "vi-vn", "zh-tw"
}

# 3. Lista de chaves que todo arquivo DEVE ter no nível principal.
REQUIRED_TOP_LEVEL_KEYS = {
    "id", "wiki_id", "name", "description", "rarity", "type",
    "subStat", "passiveName", "passiveDescription", "weaponIconUrl",
    "ascensionMaterials", "attributes"
}

# 4. Lista de palavras-chave PROIBIDAS no campo 'passiveName'.
#    Estas são as chaves padrão que não deveriam vazar para o nome da passiva.
#    Usamos um set para uma busca mais rápida.
BAD_PASSIVE_KEYWORDS = {
    # Adicione aqui todas as chaves do seu dicionário STANDARD_INFO_KEYS
    # para garantir que nenhuma delas vaze para o resultado final.
    # Exemplo (adicionei as que já encontramos):
    "Где найти:", "cómo se consigue", "หาได้จาก", "nguyên liệu tinh luyện", "имя:",
    "fonte", "source", "region", "tipo", "type"
}

# Campos que devem conter um dicionário de traduções completo.
TRANSLATABLE_FIELDS = ["name", "description", "type", "subStat",
                       "passiveName", "passiveDescription"]

# --- FUNÇÃO DE VALIDAÇÃO ---


def validate_file(filepath):
    """
    Valida um único arquivo JSON e retorna uma lista de erros.
    Se a lista estiver vazia, o arquivo está OK.
    """
    errors = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        errors.append("Arquivo não é um JSON válido.")
        return errors  # Não podemos continuar se o JSON for inválido
    except Exception as e:
        errors.append(f"Erro inesperado ao ler o arquivo: {e}")
        return errors

    # Verificação 1: Chaves obrigatórias no nível principal
    missing_keys = REQUIRED_TOP_LEVEL_KEYS - set(data.keys())
    if missing_keys:
        errors.append(
            f"Chaves obrigatórias faltando: {', '.join(missing_keys)}")

    # Verificação 2: Palavras-chave proibidas no 'passiveName'
    if 'passiveName' in data and isinstance(data['passiveName'], dict):
        for lang, name in data['passiveName'].items():
            # Normaliza o nome da passiva para a verificação
            name_for_check = re.sub(
                r'\s+', ' ', name).strip().lower().strip(":")
            if name_for_check in BAD_PASSIVE_KEYWORDS:
                errors.append(
                    f"'{lang}' em 'passiveName' contém uma palavra-chave proibida: '{name}'")

    # Verificação 3: Integridade das traduções
    for field in TRANSLATABLE_FIELDS:
        if field in data and isinstance(data[field], dict):
            found_langs = set(data[field].keys())
            if not SUPPORTED_LANGUAGES.issubset(found_langs):
                missing_langs = SUPPORTED_LANGUAGES - found_langs
                errors.append(
                    f"Traduções faltando no campo '{field}': {', '.join(missing_langs)}")
        elif field in REQUIRED_TOP_LEVEL_KEYS:
            errors.append(
                f"Campo de tradução '{field}' não é um dicionário ou não foi encontrado.")

    # Verificação 4: Tipos de dados
    if 'rarity' in data and not isinstance(data['rarity'], int):
        errors.append("'rarity' deveria ser um número inteiro (integer).")

    if 'ascensionMaterials' in data and not isinstance(data['ascensionMaterials'], list):
        errors.append("'ascensionMaterials' deveria ser uma lista (list).")

    return errors

# --- SCRIPT PRINCIPAL ---


def main():
    """
    Função principal que executa o processo de validação.
    """
    print("Iniciando validação dos arquivos JSON...")
    all_errors = {}

    if not os.path.isdir(TARGET_DIRECTORY):
        print(f"ERRO: O diretório '{TARGET_DIRECTORY}' não foi encontrado.")
        return

    for filename in os.listdir(TARGET_DIRECTORY):
        if filename.endswith('.json'):
            filepath = os.path.join(TARGET_DIRECTORY, filename)
            errors = validate_file(filepath)
            if errors:
                all_errors[filename] = errors

    print("-" * 50)
    if not all_errors:
        print("✅ Validação concluída! Nenhum erro encontrado. Todos os arquivos estão OK!")
    else:
        print(
            f"🚨 Validação concluída! Foram encontrados problemas em {len(all_errors)} arquivo(s):")
        for filename, errors in all_errors.items():
            print(f"\n--- Erros em: {filename} ---")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
    print("-" * 50)


if __name__ == '__main__':
    main()
