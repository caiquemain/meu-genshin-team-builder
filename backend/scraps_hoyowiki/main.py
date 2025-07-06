import json
import asyncio
import os
import re
import aiohttp
import subprocess
import config

# Importa as novas classes de parser especializadas
from api_client import APIClient
from character_parser import CharacterParser
from weapon_parser import WeaponParser
from material_parser import MaterialParser

# --- CONSTANTES DE ORQUESTRAÇÃO ---
LIST_API_URL = "https://sg-wiki-api.hoyolab.com/hoyowiki/genshin/wapi/get_entry_page_list"
CHARACTERS_MENU_ID = "2"
WEAPONS_MENU_ID = "4"

# Nomes dos arquivos de cache e scripts de teste
ALL_CHARACTERS_FILE = os.path.join(
    config.CACHE_DIR, "all_genshin_characters.json")
ALL_WEAPONS_FILE = os.path.join(config.CACHE_DIR, "all_genshin_weapons.json")
ALL_MATERIALS_FILE = os.path.join(config.CACHE_DIR, "materials_to_scrape.json")

WEAPON_TEST_SCRIPT = "test_weapons.py"
CHARACTER_TEST_SCRIPT = "test_characters.py"
MATERIAL_TEST_SCRIPT = "test_materials.py"
MATERIAL_DISCOVERY_SCRIPT = "discover_materials.py"
WEAPON_IMAGE_DOWNLOAD_SCRIPT = "download_weapon_images.py"
CHARACTER_IMAGE_DOWNLOAD_SCRIPT = "download_character_images.py"

# --- FUNÇÕES GENÉRICAS DE FETCH E PROCESSAMENTO ---


async def fetch_entry_list(api_client: APIClient, menu_id: str, entry_name_plural: str):
    """Busca a lista de todas as entradas (personagens ou armas) de um menu_id."""
    all_entries = []
    page_num = 1
    page_size = 30
    print(f"Iniciando a busca pela lista de {entry_name_plural}...")
    async with aiohttp.ClientSession() as session:
        while True:
            payload = {"filters": [], "menu_id": menu_id,
                       "page_num": page_num, "page_size": page_size, "use_es": True}
            print(
                f"Buscando página {page_num} da lista de {entry_name_plural}...")
            data = await api_client.post_page_list(session, LIST_API_URL, payload)
            if data and data.get('retcode') == 0 and 'list' in data.get('data', {}):
                current_page_entries = data['data']['list']
                if not current_page_entries:
                    print(f"Página {page_num} vazia. Fim da lista.")
                    break
                all_entries.extend(current_page_entries)
                total_entries = int(data['data'].get('total', 0))
                print(
                    f"Adicionados {len(current_page_entries)} itens. Total: {len(all_entries)} de {total_entries}")
                if len(all_entries) >= total_entries and total_entries > 0:
                    break
                page_num += 1
                await asyncio.sleep(0.5)
            else:
                print("Estrutura de dados inesperada ou falha na requisição.")
                break
    return all_entries


async def process_all_entries(parser, entries: list, output_dir: str, parser_func_name: str):
    """Processa uma lista de entradas e salva em arquivos individuais."""
    parser_func = getattr(parser, parser_func_name)
    print(
        f"\nIniciando o processamento de {len(entries)} itens em '{output_dir}'...")
    for entry_info in entries:
        entry_id = entry_info.get("entry_page_id") or entry_info.get("id")
        entry_name_en = entry_info.get("name")
        if not entry_id:
            print(f"Item '{entry_name_en}' sem ID válido, pulando.")
            continue
        safe_name = re.sub(r'[^a-z0-9_]+', '', entry_name_en.lower().replace(
            ' ', '_')) if entry_name_en else str(entry_id)
        output_filename = os.path.join(output_dir, f"{safe_name}.json")
        if os.path.exists(output_filename):
            print(f"Arquivo para '{entry_name_en}' já existe. Pulando.")
            continue
        print(f"Processando: {entry_name_en} (ID: {entry_id})")
        processed_data = await parser_func(str(entry_id), entry_info)
        if not processed_data:
            print(f"  -> Falha ao processar {entry_name_en}.")
            continue
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        print(f"  -> Salvo em: {output_filename}")
        await asyncio.sleep(1)


async def run_scrape_routine(parser, menu_id, list_file, output_dir, entry_name_plural, parser_func_name):
    """Encapsula a lógica de baixar e processar um tipo de entrada."""
    all_entries = []
    if os.path.exists(list_file):
        print(f"\nArquivo de lista '{list_file}' encontrado. Usando cache.")
        try:
            with open(list_file, 'r', encoding='utf-8') as f:
                all_entries = json.load(f)
        except json.JSONDecodeError:
            print("Arquivo de lista corrompido, será gerado novamente.")
            all_entries = []

    if not all_entries:
        all_entries = await fetch_entry_list(parser.api_client, menu_id, entry_name_plural)
        if all_entries:
            with open(list_file, 'w', encoding='utf-8') as f:
                json.dump(all_entries, f, indent=2, ensure_ascii=False)
            print(f"Lista de {entry_name_plural} salva em '{list_file}'.")
        else:
            print(
                f"Não foi possível buscar a lista de {entry_name_plural}. Encerrando.")
            return

    await process_all_entries(parser, all_entries, output_dir, parser_func_name)
    print(f"\nProcessamento de {entry_name_plural} concluído.")

# --- LÓGICA PRINCIPAL E MENU ---


async def main():
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    os.makedirs(config.CHARACTERS_OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.WEAPONS_OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.MATERIALS_OUTPUT_DIR, exist_ok=True)

    cookie_string = input(
        "Por favor, insira sua string de Cookie do HoYoLAB: ")
    api_client = APIClient(cookie_string=cookie_string)

    while True:
        print("\n" + "="*25)
        print("  PAINEL DE CONTROLE")
        print("="*25)
        print("\n--- 1. Baixar Dados da API ---")
        print("  1. Baixar Dados dos Personagens")
        print("  2. Baixar Dados das Armas")
        print("  3. Baixar Dados dos Materiais (Requer descoberta)")
        print("  4. Baixar TUDO (Personagens e Armas)")

        print("\n--- 2. Processar Dados Locais ---")
        print("  5. Descobrir Materiais (Analisar arquivos)")
        print("  6. Enriquecer Dados (Preencher URLs de ícones)")
        print("  7. Baixar Imagens dos Materiais")
        print("  8. Baixar Imagens das Armas")
        print("  9. Baixar Imagens dos Personagens")  # <-- NOVA OPÇÃO

        print("\n--- 3. Validar Dados ---")
        print("  10. Testar Arquivos de Personagens")
        print("  11. Testar Arquivos de Armas")
        print("  12. Testar Arquivos de Materiais")

        print("\n  13. Sair")

        choice = input("\nSua escolha (1-13): ")

        if choice == '1':
            parser = CharacterParser(api_client)
            parser.load_materials_from_disk(config.MATERIALS_OUTPUT_DIR)
            await run_scrape_routine(parser, CHARACTERS_MENU_ID, ALL_CHARACTERS_FILE, config.CHARACTERS_OUTPUT_DIR, "personagens", "parse_character_basic_info")

        elif choice == '2':
            parser = WeaponParser(api_client)
            parser.load_materials_from_disk(config.MATERIALS_OUTPUT_DIR)
            await run_scrape_routine(parser, WEAPONS_MENU_ID, ALL_WEAPONS_FILE, config.WEAPONS_OUTPUT_DIR, "armas", "parse_weapon_info")

        elif choice == '3':
            parser = MaterialParser(api_client)
            if not os.path.exists(ALL_MATERIALS_FILE):
                print(
                    f"ERRO: '{ALL_MATERIALS_FILE}' não encontrado. Execute a opção 5 primeiro.")
            else:
                with open(ALL_MATERIALS_FILE, 'r', encoding='utf-8') as f:
                    materials_to_scrape = json.load(f)
                await process_all_entries(parser, materials_to_scrape, config.MATERIALS_OUTPUT_DIR, "parse_material_info")

        elif choice == '4':
            print("\nIniciando download de personagens e armas simultaneamente...")
            char_parser = CharacterParser(api_client)
            char_parser.load_materials_from_disk(config.MATERIALS_OUTPUT_DIR)
            weapon_parser = WeaponParser(api_client)
            weapon_parser.load_materials_from_disk(config.MATERIALS_OUTPUT_DIR)

            task_chars = asyncio.create_task(run_scrape_routine(
                char_parser, CHARACTERS_MENU_ID, ALL_CHARACTERS_FILE, config.CHARACTERS_OUTPUT_DIR, "personagens", "parse_character_basic_info"))
            task_weapons = asyncio.create_task(run_scrape_routine(
                weapon_parser, WEAPONS_MENU_ID, ALL_WEAPONS_FILE, config.WEAPONS_OUTPUT_DIR, "armas", "parse_weapon_info"))
            await asyncio.gather(task_chars, task_weapons)
            print("\nDownloads simultâneos concluídos.")

        elif choice == '5':
            subprocess.run(["python", "enrich_data.py"])

        elif choice == '6':
            # Script de materiais
            subprocess.run(["python", "download_images.py"])

        elif choice == '7':
            # Script de materiais
            subprocess.run(["python", "download_images.py"])

        elif choice == '8':
            subprocess.run(["python", "download_weapon_images.py"])

        elif choice == '9':  # <-- LÓGICA DA NOVA OPÇÃO
            print("\nExecutando script de download de imagens de personagens...")
            subprocess.run(["python", CHARACTER_IMAGE_DOWNLOAD_SCRIPT])

        elif choice == '10':
            subprocess.run(["python", CHARACTER_TEST_SCRIPT])

        elif choice == '11':
            subprocess.run(["python", WEAPON_TEST_SCRIPT])

        elif choice == '12':
            subprocess.run(["python", MATERIAL_TEST_SCRIPT])

        elif choice == '13':
            print("Encerrando o programa.")
            break

        else:
            print("Opção inválida. Por favor, escolha um número de 1 a 13.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário.")
