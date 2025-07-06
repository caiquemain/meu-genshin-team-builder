import os
import json
import config  # Importa nossas configurações centralizadas


def validate_character_file(filepath):
    """
    Valida um único arquivo JSON de personagem e retorna uma lista de erros.
    """
    errors = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return [f"Erro ao ler JSON: {e}"]

    # Verificação 1: Chaves obrigatórias
    missing_keys = config.CHARACTERS_REQUIRED_KEYS - set(data.keys())
    if missing_keys:
        errors.append(
            f"Chaves obrigatórias faltando: {', '.join(missing_keys)}")

    # Verificação 2: Traduções nos campos principais
    for field in config.CHARACTERS_TRANSLATABLE_FIELDS:
        if field in data and isinstance(data[field], dict):
            found_langs = set(data[field].keys())
            if not config.SUPPORTED_LANGUAGES.issubset(found_langs):
                missing_langs = config.SUPPORTED_LANGUAGES - found_langs
                errors.append(
                    f"Traduções faltando no campo '{field}': {', '.join(missing_langs)}")
        elif field in config.CHARACTERS_REQUIRED_KEYS:
            errors.append(
                f"Campo de tradução '{field}' não é um dicionário ou não foi encontrado.")

    # Verificação 3: Traduções aninhadas
    for list_name in ['talents', 'constellations']:
        if list_name in data and isinstance(data[list_name], list):
            for i, item in enumerate(data[list_name]):
                for field in ['name', 'description']:
                    if field in item and isinstance(item[field], dict):
                        missing_langs = config.SUPPORTED_LANGUAGES - \
                            set(item[field].keys())
                        if missing_langs:
                            errors.append(
                                f"{list_name[:-1].capitalize()} #{i+1}: Faltando traduções em '{field}'")
                    elif field in item:
                        errors.append(
                            f"{list_name[:-1].capitalize()} #{i+1}: Campo '{field}' não é um dicionário.")

    # Verificação 4: iconUrl nos materiais
    if 'ascensionMaterials' in data and isinstance(data.get('ascensionMaterials'), list):
        for i, level_group in enumerate(data['ascensionMaterials']):
            for material in level_group.get('materials', []):
                if not material.get('iconUrl'):
                    mat_name = material.get('name', {}).get(
                        'en-us', f"ID {material.get('id')}")
                    errors.append(
                        f"Material de Ascensão '{mat_name}' está com iconUrl nulo ou ausente.")

    if 'talentMaterials' in data and isinstance(data.get('talentMaterials'), list):
        for talent_group in data['talentMaterials']:
            talent_name = talent_group.get('talentName', {}).get(
                'en-us', 'Nome de talento desconhecido')
            for level_group in talent_group.get('materials', []):
                for item in level_group.get('items', []):
                    if not item.get('iconUrl'):
                        item_name = item.get('name', {}).get(
                            'en-us', f"ID {item.get('id')}")
                        errors.append(
                            f"Material para Talento '{talent_name}' (Nível {level_group.get('level')}) - item '{item_name}' está com iconUrl nulo ou ausente.")

    return errors


def main():
    """Função principal para executar os testes de personagens."""
    print("Iniciando validação dos arquivos de PERSONAGENS...")
    all_errors = {}

    # Usa a variável de configuração para o diretório
    if not os.path.isdir(config.CHARACTERS_OUTPUT_DIR):
        print(
            f"ERRO: O diretório '{config.CHARACTERS_OUTPUT_DIR}' não foi encontrado.")
        return

    for filename in os.listdir(config.CHARACTERS_OUTPUT_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(config.CHARACTERS_OUTPUT_DIR, filename)

            # AQUI ESTÁ A CORREÇÃO:
            # A chamada agora usa o nome correto da função que definimos acima.
            errors = validate_character_file(filepath)

            if errors:
                all_errors[filename] = errors

    print("-" * 50)
    if not all_errors:
        print("✅ Validação concluída! Nenhum erro encontrado.")
    else:
        print(
            f"🚨 Validação concluída! Problemas em {len(all_errors)} arquivo(s):")
        for filename, errors in all_errors.items():
            print(f"\n--- Erros em: {filename} ---")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
    print("-" * 50)


# Bloco padrão para permitir que o script seja executável
if __name__ == '__main__':
    main()
