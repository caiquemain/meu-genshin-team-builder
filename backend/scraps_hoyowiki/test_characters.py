import os
import json

# --- CONFIGURAÇÃO ---

# 1. Altere para o nome da pasta onde seus arquivos JSON de PERSONAGENS estão.
TARGET_DIRECTORY = 'characters_data'

# 2. Lista de idiomas que todos os campos de tradução devem ter.
SUPPORTED_LANGUAGES = {
    "pt-pt", "en-us", "ja-jp", "zh-cn", "ko-kr", "ru-ru",
    "de-de", "fr-fr", "es-es", "id-id", "th-th", "vi-vn", "zh-tw"
}

# 3. Lista de chaves que todo arquivo de PERSONAGEM deve ter.
REQUIRED_TOP_LEVEL_KEYS = {
    "id", "wiki_id", "name", "title", "description", "rarity",
    "vision", "weapon", "characterIconUrl", "elementIconUrl",
    "constellationNameOfficial", "specialDish", "namecard", "constellations",
    "talents", "talentAttributes", "talentMaterials", "affiliation",
    "birthday", "ascensionMaterials", "attributes"
}

# 4. Campos no nível principal que devem ser dicionários de tradução.
TRANSLATABLE_FIELDS = [
    "name", "title", "description", "vision", "weapon",
    "constellationNameOfficial", "affiliation", "birthday"
]

# --- FUNÇÃO DE VALIDAÇÃO ---

def validate_file(filepath):
    """
    Valida um único arquivo JSON de personagem e retorna uma lista de erros.
    """
    errors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        errors.append("Arquivo não é um JSON válido.")
        return errors
    except Exception as e:
        errors.append(f"Erro inesperado ao ler o arquivo: {e}")
        return errors

    # Verificação 1: Chaves obrigatórias no nível principal
    missing_keys = REQUIRED_TOP_LEVEL_KEYS - set(data.keys())
    if missing_keys:
        errors.append(f"Chaves obrigatórias faltando: {', '.join(missing_keys)}")

    # Verificação 2: Integridade das traduções nos campos principais
    for field in TRANSLATABLE_FIELDS:
        if field in data and isinstance(data[field], dict):
            found_langs = set(data[field].keys())
            if not SUPPORTED_LANGUAGES.issubset(found_langs):
                missing_langs = SUPPORTED_LANGUAGES - found_langs
                errors.append(f"Traduções faltando no campo principal '{field}': {', '.join(missing_langs)}")
        elif field in REQUIRED_TOP_LEVEL_KEYS:
             errors.append(f"Campo de tradução '{field}' não é um dicionário ou não foi encontrado.")

    # Verificação 3: Integridade das traduções DENTRO da lista de 'talents'
    if 'talents' in data and isinstance(data['talents'], list):
        for i, talent in enumerate(data['talents']):
            # Checa o nome do talento
            if 'name' in talent and isinstance(talent['name'], dict):
                missing_langs = SUPPORTED_LANGUAGES - set(talent['name'].keys())
                if missing_langs:
                    errors.append(f"Talento #{i+1}: Faltando traduções para 'name': {', '.join(missing_langs)}")
            else:
                errors.append(f"Talento #{i+1}: Campo 'name' faltando ou não é um dicionário.")
            
            # Checa a descrição do talento
            if 'description' in talent and isinstance(talent['description'], dict):
                missing_langs = SUPPORTED_LANGUAGES - set(talent['description'].keys())
                if missing_langs:
                    errors.append(f"Talento #{i+1}: Faltando traduções para 'description': {', '.join(missing_langs)}")
            else:
                 errors.append(f"Talento #{i+1}: Campo 'description' faltando ou não é um dicionário.")

    # Verificação 4: Integridade das traduções DENTRO da lista de 'constellations'
    if 'constellations' in data and isinstance(data['constellations'], list):
        for i, const in enumerate(data['constellations']):
            if 'name' in const and isinstance(const['name'], dict):
                 missing_langs = SUPPORTED_LANGUAGES - set(const['name'].keys())
                 if missing_langs:
                    errors.append(f"Constelação #{i+1}: Faltando traduções para 'name': {', '.join(missing_langs)}")
            else:
                errors.append(f"Constelação #{i+1}: Campo 'name' faltando ou não é um dicionário.")

            if 'description' in const and isinstance(const['description'], dict):
                 missing_langs = SUPPORTED_LANGUAGES - set(const['description'].keys())
                 if missing_langs:
                    errors.append(f"Constelação #{i+1}: Faltando traduções para 'description': {', '.join(missing_langs)}")
            else:
                errors.append(f"Constelação #{i+1}: Campo 'description' faltando ou não é um dicionário.")

    # Verificação 5: Tipos de dados
    if 'rarity' in data and not isinstance(data['rarity'], int):
        errors.append("'rarity' deveria ser um número inteiro (integer).")
    
    for list_key in ['constellations', 'talents', 'ascensionMaterials', 'attributes']:
        if list_key in data and not isinstance(data[list_key], list):
             errors.append(f"'{list_key}' deveria ser uma lista (list).")

    return errors

# --- SCRIPT PRINCIPAL ---

def main():
    """
    Função principal que executa o processo de validação.
    """
    print("Iniciando validação dos arquivos de PERSONAGENS...")
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
        print("✅ Validação concluída! Nenhum erro encontrado. Todos os arquivos de personagens estão OK!")
    else:
        print(f"🚨 Validação concluída! Foram encontrados problemas em {len(all_errors)} arquivo(s):")
        for filename, errors in all_errors.items():
            print(f"\n--- Erros em: {filename} ---")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
    print("-" * 50)


if __name__ == '__main__':
    main()