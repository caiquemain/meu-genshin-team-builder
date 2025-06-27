# get_all_characters.py
import asyncio
import json
import os
import time
from api_client import APIClient

# URL do endpoint que lista as entradas
LIST_API_URL = "https://sg-wiki-api.hoyolab.com/hoyowiki/genshin/wapi/get_entry_page_list"


async def fetch_character_list(api_client: APIClient):
    """
    Busca a lista de todos os personagens da API da HoYoWiki.
    """
    all_characters = []
    page_num = 1
    page_size = 30

    print("Iniciando a busca pela lista de personagens...")

    while True:
        payload = {
            "filters": [],
            "menu_id": "2",  # Menu ID para "Character Archive"
            "page_num": page_num,
            "page_size": page_size,
            "use_es": True
        }

        print(f"Buscando página {page_num} da lista de personagens...")

        # Usa o cliente de API para fazer a requisição POST
        data = await api_client.post_page_list(LIST_API_URL, payload) # type: ignore

        if data and 'data' in data and 'list' in data['data']:
            current_page_entries = data['data']['list']

            if not current_page_entries:
                print(f"Página {page_num} vazia. Fim dos dados.")
                break

            all_characters.extend(current_page_entries)

            total_entries = int(data['data'].get('total', 0))
            print(
                f"Adicionados {len(current_page_entries)} personagens. Total até agora: {len(all_characters)} de {total_entries}")

            if len(all_characters) >= total_entries:
                print("Todos os personagens foram coletados.")
                break

            page_num += 1
            # Pequeno atraso para não sobrecarregar a API
            await asyncio.sleep(0.5)
        else:
            print("Estrutura de dados inesperada ou 'data'/'list' ausente. Parando.")
            break

    return all_characters


async def run_character_list_fetcher():
    # Pede o cookie apenas para este script
    cookie_string = input(
        "Por favor, insira a sua string de Cookie do HoYoLAB para buscar a lista de personagens: ")
    api_client = APIClient(cookie_string=cookie_string)

    characters = await fetch_character_list(api_client)

    if characters:
        # Garante que a pasta 'data' existe
        os.makedirs('data', exist_ok=True)
        output_file = os.path.join('data', 'all_genshin_characters.json')

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(characters, f, indent=2, ensure_ascii=False)

        print(
            f"\nBusca concluída! {len(characters)} personagens salvos em '{output_file}'")

if __name__ == "__main__":
    asyncio.run(run_character_list_fetcher())
