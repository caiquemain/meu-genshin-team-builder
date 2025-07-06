import os
import json
import config


def validate_material_file(filepath):
    """
    Valida um único arquivo JSON de material e retorna uma lista de erros.
    """
    errors = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return [f"Erro ao ler JSON: {e}"]

    # Verificação 1: Chaves obrigatórias
    missing_keys = config.MATERIALS_REQUIRED_KEYS - set(data.keys())
    if missing_keys:
        errors.append(
            f"Chaves obrigatórias faltando: {', '.join(missing_keys)}")

    # Verificação 2: 'iconUrl' não pode ser nulo ou vazio
    if not data.get('iconUrl'):
        errors.append("O campo 'iconUrl' está nulo ou ausente.")

    # Verificação 3: Integridade das traduções
    for field in config.MATERIALS_TRANSLATABLE_FIELDS:
        if field not in data:
            continue  # O erro de chave faltando já foi pego acima

        field_data = data[field]
        if not isinstance(field_data, dict):
            errors.append(
                f"O campo '{field}' deveria ser um dicionário de traduções.")
            continue

        found_langs = set(field_data.keys())
        if not config.SUPPORTED_LANGUAGES.issubset(found_langs):
            missing_langs = config.SUPPORTED_LANGUAGES - found_langs
            errors.append(
                f"Traduções faltando no campo '{field}': {', '.join(missing_langs)}")

    return errors


def main():
    """Função principal para executar os testes de materiais."""
    print("Iniciando validação dos arquivos de MATERIAIS...")
    all_errors = {}

    if not os.path.isdir(config.MATERIALS_OUTPUT_DIR):
        print(
            f"ERRO: O diretório '{config.MATERIALS_OUTPUT_DIR}' não foi encontrado.")
        return

    for filename in os.listdir(config.MATERIALS_OUTPUT_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(config.MATERIALS_OUTPUT_DIR, filename)
            errors = validate_material_file(filepath)
            if errors:
                all_errors[filename] = errors

    print("-" * 50)
    if not all_errors:
        print("✅ Validação de materiais concluída! Nenhum erro encontrado.")
    else:
        print(
            f"🚨 Validação concluída! Problemas em {len(all_errors)} arquivo(s) de materiais:")
        for filename, errors in all_errors.items():
            print(f"\n--- Erros em: {filename} ---")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
    print("-" * 50)


if __name__ == '__main__':
    main()
