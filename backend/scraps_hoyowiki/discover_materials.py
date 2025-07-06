import os
import json

# Configuração das pastas de onde vamos ler os dados
CHARACTERS_DATA_DIR = 'characters_data'
WEAPONS_DATA_DIR = 'weapons_data'
OUTPUT_FILE = os.path.join('data', 'materials_to_scrape.json')


def discover_materials():
    """
    Lê todos os arquivos JSON de personagens e armas para encontrar
    todos os materiais de ascensão e talento únicos, usando o wiki_id.
    """
    # Usaremos um dicionário para evitar duplicatas, com o ID NUMÉRICO como chave
    unique_materials = {}

    directories_to_scan = [CHARACTERS_DATA_DIR, WEAPONS_DATA_DIR]

    print("Iniciando a descoberta de materiais únicos...")

    for directory in directories_to_scan:
        if not os.path.isdir(directory):
            print(f"Aviso: Diretório '{directory}' não encontrado. Pulando.")
            continue

        print(f"Analisando diretório: '{directory}'")
        for filename in os.listdir(directory):
            if not filename.endswith('.json'):
                continue

            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Função auxiliar para adicionar um material ao nosso set de descoberta
                def add_material_to_discovery(material):
                    # --- AQUI ESTÁ A CORREÇÃO PRINCIPAL ---
                    # Priorizamos o wiki_id (o número) para a descoberta.
                    numeric_id = material.get('wiki_id')

                    if numeric_id and numeric_id not in unique_materials:
                        english_name = material.get(
                            'name', {}).get('en-us', 'Unknown')
                        unique_materials[numeric_id] = {
                            # O entry_page_id DEVE ser o ID numérico para o scraper funcionar
                            "entry_page_id": numeric_id,
                            "name": english_name  # Guardamos o nome para referência
                        }

                # Extrai de 'ascensionMaterials'
                if 'ascensionMaterials' in data and data['ascensionMaterials']:
                    for level_group in data['ascensionMaterials']:
                        for material in level_group.get('materials', []):
                            add_material_to_discovery(material)

                # Extrai de 'talentMaterials' (apenas para personagens)
                if 'talentMaterials' in data and data['talentMaterials']:
                    for talent_group in data['talentMaterials']:
                        for level_group in talent_group.get('materials', []):
                            for material in level_group.get('items', []):
                                add_material_to_discovery(material)

    # Converte o dicionário de volta para uma lista para salvar no JSON
    materials_list = list(unique_materials.values())

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(materials_list, f, indent=2, ensure_ascii=False)

    print(f"\nDescoberta concluída!")
    print(f"Encontrados {len(materials_list)} materiais únicos.")
    print(f"Lista salva em: '{OUTPUT_FILE}'")


if __name__ == '__main__':
    discover_materials()
