# main.py (versão automatizada)
import json
import asyncio
import os
import time
import aiohttp

from config import ALL_CHARACTERS_FILE
from api_client import APIClient
from data_parser import DataParser

# URL para buscar a lista de personagens, movida para cá
LIST_API_URL = "https://sg-wiki-api.hoyolab.com/hoyowiki/genshin/wapi/get_entry_page_list"


async def fetch_character_list(api_client: APIClient):
    """
    Busca a lista de todos os personagens da API e salva em um arquivo JSON.
    """
    all_characters = []
    page_num = 1
    page_size = 30  # A API parece retornar um máximo de 30 por página

    print("Iniciando a busca pela lista de personagens...")

    async with aiohttp.ClientSession() as session:
        while True:
            payload = {
                "filters": [],
                "menu_id": "2",  # Menu ID para "Character Archive"
                "page_num": page_num,
                "page_size": page_size,
                "use_es": True
            }

            print(f"Buscando página {page_num} da lista de personagens...")
            data = await api_client.post_page_list(session, LIST_API_URL, payload)

            if data and data.get('retcode') == 0 and 'list' in data.get('data', {}):
                current_page_entries = data['data']['list']
                if not current_page_entries:
                    print(
                        f"Página {page_num} vazia. Fim da lista de personagens.")
                    break

                all_characters.extend(current_page_entries)
                total_entries = int(data['data'].get('total', 0))
                print(
                    f"Adicionados {len(current_page_entries)} personagens. Total até agora: {len(all_characters)} de {total_entries}")

                if len(all_characters) >= total_entries and total_entries > 0:
                    print("Todos os personagens foram coletados.")
                    break

                page_num += 1
                await asyncio.sleep(0.5)  # Atraso para não sobrecarregar a API
            else:
                print(
                    "Estrutura de dados inesperada ou falha na requisição. Parando a busca.")
                break

    if all_characters:
        # Garante que a pasta 'data' existe
        os.makedirs('data', exist_ok=True)
        with open(ALL_CHARACTERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_characters, f, indent=2, ensure_ascii=False)
        print(
            f"\nBusca concluída! {len(all_characters)} personagens salvos em '{ALL_CHARACTERS_FILE}'")

    return all_characters


async def main():
    # Cria as pastas necessárias no início
    os.makedirs('data', exist_ok=True)
    output_directory = 'characters_data'
    os.makedirs(output_directory, exist_ok=True)

    all_characters = []
    # Verifica se o arquivo principal de personagens já existe
    if os.path.exists(ALL_CHARACTERS_FILE):
        print(f"Arquivo '{ALL_CHARACTERS_FILE}' encontrado.")
        try:
            with open(ALL_CHARACTERS_FILE, 'r', encoding='utf-8') as f:
                all_characters = json.load(f)
        except json.JSONDecodeError:
            print("Arquivo de personagens está corrompido. Ele será gerado novamente.")
            all_characters = []  # Força a recriação

    # Se o arquivo não existe ou está vazio/corrompido, busca na API
    if not all_characters:
        print(
            f"\nArquivo '{ALL_CHARACTERS_FILE}' não encontrado ou inválido. Ele será criado agora.")
        cookie_string_for_list = input(
            "Por favor, insira a sua string de Cookie do HoYoLAB para buscar a lista de personagens: ")
        client_for_list = APIClient(cookie_string=cookie_string_for_list)
        all_characters = await fetch_character_list(client_for_list)
        if not all_characters:
            print("Não foi possível buscar a lista de personagens. Encerrando o script.")
            return

    # Pergunta pelo cookie uma única vez para o processo principal
    cookie_string = input(
        "\nPor favor, insira a sua string de Cookie do HoYoLAB para buscar os detalhes dos personagens: ")
    api_client = APIClient(cookie_string=cookie_string)
    parser = DataParser(api_client)

    print(
        f"\nIniciando o processamento de {len(all_characters)} personagens...")

    for char_info in all_characters:
        char_id = char_info.get("entry_page_id")
        char_name_en = char_info.get("name")

        if not char_id:
            print(
                f"Personagem '{char_name_en}' não possui 'entry_page_id', pulando.")
            continue

        # Define o nome do arquivo de saída
        safe_char_name = "".join(c for c in char_name_en if c.isalnum() or c in (
            ' ', '_')).rstrip().replace(' ', '_').lower()
        output_filename = os.path.join(
            output_directory, f"{safe_char_name}.json")

        # Pula o download se o arquivo já existir
        if os.path.exists(output_filename):
            print(
                f"Arquivo para {char_name_en} já existe em '{output_filename}'. Pulando.")
            continue

        print(f"Processando e salvando: {char_name_en} (ID: {char_id})")
        processed_char_data = await parser.parse_character_basic_info(char_id, char_info)

        if not processed_char_data:
            print(
                f"  -> Falha ao processar {char_name_en}. Nenhum dado foi salvo.")
            continue

        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(processed_char_data, f, ensure_ascii=False, indent=2)

        print(f"  Salvo em: {output_filename}")
        # Adiciona um pequeno delay para não sobrecarregar a API
        await asyncio.sleep(1)

    print(
        f"\nProcessamento concluído. Arquivos salvos na pasta '{output_directory}'.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário.")
