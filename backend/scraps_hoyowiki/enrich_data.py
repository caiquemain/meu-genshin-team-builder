import os
import json
import config


def load_materials_database():
    """
    Carrega todos os arquivos de materiais em um dicionário para busca rápida,
    usando o campo 'id' (o slug amigável) como a chave principal.
    """
    db = {}
    if not os.path.isdir(config.MATERIALS_OUTPUT_DIR):
        print(
            f"ERRO: Diretório de materiais '{config.MATERIALS_OUTPUT_DIR}' não encontrado.")
        return None

    print(
        f"Carregando banco de dados de materiais de '{config.MATERIALS_OUTPUT_DIR}'...")
    for filename in os.listdir(config.MATERIALS_OUTPUT_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(config.MATERIALS_OUTPUT_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    material_data = json.load(f)

                    # Usa o 'id' (slug) como a chave do nosso banco de dados.
                    if 'id' in material_data and material_data['id']:
                        db[material_data['id']] = material_data
                    else:
                        print(
                            f"  Aviso: Material no arquivo {filename} não possui um 'id' válido. Pulando.")

            except (IOError, json.JSONDecodeError) as e:
                print(
                    f"  Aviso: Falha ao carregar o material {filename}. Erro: {e}")

    print(f"Carregados {len(db)} materiais no banco de dados.")
    return db


def enrich_file(filepath, materials_db):
    """Enriquece um único arquivo de personagem ou arma."""
    was_modified = False
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(
            f"ERRO: Não foi possível ler o arquivo {os.path.basename(filepath)}. Erro: {e}")
        return False

    def enrich_item(item):
        nonlocal was_modified
        if item.get('iconUrl') is None:
            slug_id = item.get('id')
            wiki_id = item.get('wiki_id')

            if slug_id and slug_id in materials_db and materials_db[slug_id].get('iconUrl'):
                item['iconUrl'] = materials_db[slug_id]['iconUrl']
                was_modified = True
            # CORREÇÃO: Usa a variável do arquivo de configuração
            elif wiki_id and wiki_id in config.MANUAL_FALLBACKS:
                item['iconUrl'] = config.MANUAL_FALLBACKS[wiki_id].get('iconUrl')
                was_modified = True

    # Processa 'ascensionMaterials' para personagens e armas
    if 'ascensionMaterials' in data:
        for level_group in data.get('ascensionMaterials', []):
            for material in level_group.get('materials', []):
                enrich_item(material)

    # Processa 'talentMaterials' para personagens
    if 'talentMaterials' in data:
        for talent_group in data.get('talentMaterials', []):
            for level_group in talent_group.get('materials', []):
                for item in level_group.get('items', []):
                    enrich_item(item)

    # Processa 'specialDish' e 'namecard' para personagens
    for section in ['specialDish', 'namecard']:
        if section in data and isinstance(data[section], dict):
            enrich_item(data[section])

    if was_modified:
        print(f"  Enriquecendo '{os.path.basename(filepath)}'...")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return was_modified


def main():
    print("--- Script de Enriquecimento de Dados ---")
    materials_db = load_materials_database()

    if materials_db is None:
        print("Não foi possível carregar o banco de dados de materiais. Encerrando.")
        return

    # Processa Personagens e Armas
    for dir_name, type_name in [(config.CHARACTERS_OUTPUT_DIR, "personagens"), (config.WEAPONS_OUTPUT_DIR, "armas")]:
        if os.path.isdir(dir_name):
            print(
                f"\nIniciando enriquecimento dos arquivos em '{dir_name}'...")
            updated_count = sum(1 for f in os.listdir(dir_name) if f.endswith(
                '.json') and enrich_file(os.path.join(dir_name, f), materials_db))
            print(
                f"Enriquecimento de {type_name} concluído. {updated_count} arquivo(s) foram atualizados.")

    print("\nProcesso finalizado.")


if __name__ == '__main__':
    main()
