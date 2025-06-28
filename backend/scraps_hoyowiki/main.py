# main.py (versão final com menu de controle que chama scripts externos)
import json
import asyncio
import os
import aiohttp
import subprocess  # Módulo para chamar outros scripts

# Importações dos seus módulos locais
from api_client import APIClient
from data_parser import DataParser

# --- CONFIGURAÇÃO GERAL ---
LIST_API_URL = "https://sg-wiki-api.hoyolab.com/hoyowiki/genshin/wapi/get_entry_page_list"
CHARACTERS_MENU_ID = "2"
WEAPONS_MENU_ID = "4"

# Nomes dos scripts de teste
WEAPON_TEST_SCRIPT = "test_weapons.py"
CHARACTER_TEST_SCRIPT = "test_characters.py"

# Pastas e arquivos de cache
CACHE_DIR = "data"
CHARACTERS_OUTPUT_DIR = 'characters_data'
WEAPONS_OUTPUT_DIR = 'weapons_data'
ALL_CHARACTERS_FILE = os.path.join(CACHE_DIR, "all_genshin_characters.json")
ALL_WEAPONS_FILE = os.path.join(CACHE_DIR, "all_genshin_weapons.json")

# --- FUNÇÕES DE SCRAPING (do seu script original) ---


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
                    f"Adicionados {len(current_page_entries)} itens. Total até agora: {len(all_entries)} de {total_entries}")

                if len(all_entries) >= total_entries and total_entries > 0:
                    print(
                        f"Todos os {total_entries} {entry_name_plural} foram coletados.")
                    break
                page_num += 1
                await asyncio.sleep(0.5)
            else:
                print("Estrutura de dados inesperada ou falha na requisição. Parando.")
                break
    return all_entries


async def process_all_entries(parser: DataParser, entries: list, output_dir: str, parser_func_name: str):
    """Processa uma lista de entradas e salva em arquivos individuais."""
    parser_func = getattr(parser, parser_func_name)

    print(
        f"\nIniciando o processamento e salvamento de {len(entries)} itens em '{output_dir}'...")

    for entry_info in entries:
        entry_id = entry_info.get("entry_page_id")
        entry_name_en = entry_info.get("name")

        if not entry_id:
            print(
                f"Item '{entry_name_en}' não possui 'entry_page_id', pulando.")
            continue

        safe_name = "".join(c for c in entry_name_en if c.isalnum() or c in (
            ' ', '_')).rstrip().replace(' ', '_').lower()
        output_filename = os.path.join(output_dir, f"{safe_name}.json")

        if os.path.exists(output_filename):
            print(f"Arquivo para '{entry_name_en}' já existe. Pulando.")
            continue

        print(f"Processando e salvando: {entry_name_en} (ID: {entry_id})")
        processed_data = await parser_func(str(entry_id), entry_info)

        if not processed_data:
            print(
                f"  -> Falha ao processar {entry_name_en}. Nenhum dado foi salvo.")
            continue

        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)

        print(f"  -> Salvo em: {output_filename}")
        await asyncio.sleep(1)

# --- ROTINAS DE EXECUÇÃO ---


async def run_scrape_routine(api_client: APIClient, parser: DataParser, menu_id, list_file, output_dir, entry_name_plural, parser_func_name):
    """Encapsula a lógica de baixar e processar um tipo de entrada."""
    all_entries = []
    if os.path.exists(list_file):
        print(f"\nArquivo de lista '{list_file}' encontrado. Usando cache.")
        try:
            with open(list_file, 'r', encoding='utf-8') as f:
                all_entries = json.load(f)
        except json.JSONDecodeError:
            print("Arquivo de lista está corrompido. Ele será gerado novamente.")
            all_entries = []

    if not all_entries:
        all_entries = await fetch_entry_list(api_client, menu_id, entry_name_plural)
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
    # PRIMEIRO PASSO: Criar todas as pastas necessárias na inicialização.
    # Esta é a correção para o FileNotFoundError.
    print("Verificando e criando pastas de saída...")
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(CHARACTERS_OUTPUT_DIR, exist_ok=True)
    os.makedirs(WEAPONS_OUTPUT_DIR, exist_ok=True)

    # O Cookie é solicitado apenas uma vez no início
    cookie_string = input(
        "Por favor, insira sua string de Cookie do HoYoLAB: ")
    api_client = APIClient(cookie_string=cookie_string)
    parser = DataParser(api_client)

    while True:
        print("\n" + "="*25)
        print("  PAINEL DE CONTROLE")
        print("="*25)
        print("\n--- Scraping (Baixar Dados) ---")
        print("  1. Baixar Dados dos Personagens")
        print("  2. Baixar Dados das Armas")
        print("  3. Baixar TUDO (Personagens e Armas)")
        print("\n--- Validação (Testar Arquivos) ---")
        print("  4. Testar Arquivos de Personagens")
        print("  5. Testar Arquivos de Armas")
        print("  6. Testar TUDO (Personagens e Armas)")
        print("\n--- Ciclo Completo ---")
        print("  7. Executar TUDO (Baixar e depois Testar)")
        print("\n  8. Sair")

        choice = input("\nSua escolha (1-8): ")

        if choice == '1':
            await run_scrape_routine(api_client, parser, CHARACTERS_MENU_ID, ALL_CHARACTERS_FILE, CHARACTERS_OUTPUT_DIR, "personagens", "parse_character_basic_info")

        elif choice == '2':
            await run_scrape_routine(api_client, parser, WEAPONS_MENU_ID, ALL_WEAPONS_FILE, WEAPONS_OUTPUT_DIR, "armas", "parse_weapon_info")

        elif choice == '3':
            print("\nIniciando download de personagens e armas simultaneamente...")
            task_chars = asyncio.create_task(run_scrape_routine(api_client, parser, CHARACTERS_MENU_ID,
                                             ALL_CHARACTERS_FILE, CHARACTERS_OUTPUT_DIR, "personagens", "parse_character_basic_info"))
            task_weapons = asyncio.create_task(run_scrape_routine(
                api_client, parser, WEAPONS_MENU_ID, ALL_WEAPONS_FILE, WEAPONS_OUTPUT_DIR, "armas", "parse_weapon_info"))
            await asyncio.gather(task_chars, task_weapons)
            print("\nDownloads simultâneos concluídos.")

        elif choice == '4':
            print("\nExecutando script de teste de personagens...")
            subprocess.run(["python", CHARACTER_TEST_SCRIPT])

        elif choice == '5':
            print("\nExecutando script de teste de armas...")
            subprocess.run(["python", WEAPON_TEST_SCRIPT])

        elif choice == '6':
            print("\n--- EXECUTANDO TODOS OS TESTES ---")
            print("\n[TESTE DE PERSONAGENS]")
            subprocess.run(["python", CHARACTER_TEST_SCRIPT])
            print("\n[TESTE DE ARMAS]")
            subprocess.run(["python", WEAPON_TEST_SCRIPT])
            print("\n--- FIM DOS TESTES ---")

        elif choice == '7':
            print("\n--- CICLO COMPLETO: BAIXANDO TUDO ---")
            task_chars = asyncio.create_task(run_scrape_routine(api_client, parser, CHARACTERS_MENU_ID,
                                             ALL_CHARACTERS_FILE, CHARACTERS_OUTPUT_DIR, "personagens", "parse_character_basic_info"))
            task_weapons = asyncio.create_task(run_scrape_routine(
                api_client, parser, WEAPONS_MENU_ID, ALL_WEAPONS_FILE, WEAPONS_OUTPUT_DIR, "armas", "parse_weapon_info"))
            await asyncio.gather(task_chars, task_weapons)

            print("\n--- CICLO COMPLETO: TESTANDO TUDO ---")
            print("\n[TESTE DE PERSONAGENS]")
            subprocess.run(["python", CHARACTER_TEST_SCRIPT])
            print("\n[TESTE DE ARMAS]")
            subprocess.run(["python", WEAPON_TEST_SCRIPT])
            print("\n--- CICLO COMPLETO FINALIZADO ---")

        elif choice == '8':
            print("Encerrando o programa.")
            break

        else:
            print("Opção inválida. Por favor, escolha um número de 1 a 8.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário.")
