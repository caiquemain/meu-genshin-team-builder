import requests
import json
import time

# 1. URL do Endpoint da API
url = "https://sg-wiki-api.hoyolab.com/hoyowiki/genshin/wapi/get_entry_page_list"

# 2. Cabeçalhos (Headers) da Requisição
# ATENÇÃO: O cookie é sensível e pode expirar. Você pode precisar atualizá-lo
# se o script parar de funcionar após um tempo.
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es;q=0.5",
    "content-type": "application/json;charset=UTF-8",
    "cookie": "_HYVUUID=345b6926-b782-4792-9cf2-78b5df5cb2ad; _MHYUUID=3ae4d949-0b89-4c41-81f6-291a7fcdd68b; ltmid_v2=1t5rehl9oe_hy; ltuid_v2=10372499; ltoken_v2=v2_CAISDGNpZWJod3pwcnBxOBokMzQ1YjY5MjYtYjc4Mi00OTkyLTljZjItNzhiNWRmNWNiMmFkIK297cAGKOejk7wGMJOL-QRCDGhrcnBnX2dsb2JhbA.rV4baAAAAAAB.MEUCIHvYhDBKf_NIp8ysrEBTA9bcmktAu0Rbi4XdCelmPRdpAiEAwAlSRLcc6EDDXKFvDa7O30Y8-ER7Rz0Ip7u-1Efz_Ow; HYV_LOGIN_PLATFORM_OPTIONAL_AGREEMENT={\"content\":[]}; HYV_LOGIN_PLATFORM_LOAD_TIMEOUT={}; mi18nLang=pt-pt; DEVICEFP=00000000000; HYV_LOGIN_PLATFORM_TRACKING_MAP={\"sourceValue\":\"165\"}; HYV_LOGIN_PLATFORM_LIFECYCLE_ID={\"value\":\"1603fe1d-ac5b-4531-82e0-0561714de2e8\"}",
    "origin": "https://wiki.hoyolab.com",
    "priority": "u=1, i",
    "referer": "https://wiki.hoyolab.com/",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
    "x-rpc-language": "pt-pt",
    "x-rpc-wiki_app": "genshin"
}

# Lista para armazenar todos os personagens
all_characters = []
page_num = 1
page_size = 30  # Mantemos o page_size fixo em 30, como a API responde

print("Iniciando a raspagem de dados...")

while True:
    # 3. Corpo da Requisição (Payload) para a página atual
    payload = {
        "filters": [],
        "menu_id": "2",  # Menu de Personagens
        "page_num": page_num,
        "page_size": page_size,
        "use_es": True
    }

    print(f"Buscando página {page_num}...")

    # 4. Fazendo a Requisição POST
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Levanta erro para status 4xx/5xx

        # 5. Processando a Resposta
        data = response.json()

        if data and 'data' in data and 'list' in data['data']:
            current_page_entries = data['data']['list']
            # Garantir que 'total' é um número
            total_entries = int(data['data'].get('total', 0))

            if not current_page_entries:
                print(f"Página {page_num} vazia. Fim dos dados.")
                # Sai do loop se a lista estiver vazia (não há mais personagens)
                break

            for entry in current_page_entries:
                character_info = {}
                character_info['name'] = entry.get('name', 'N/A')
                character_info['entry_page_id'] = entry.get(
                    'entry_page_id', 'N/A')
                character_info['icon_url'] = entry.get('icon_url', 'N/A')

                filter_values = entry.get('filter_values', {})

                character_info['vision'] = filter_values.get(
                    'character_vision', {}).get('values', ['N/A'])[0]
                character_info['weapon'] = filter_values.get(
                    'character_weapon', {}).get('values', ['N/A'])[0]
                character_info['region'] = filter_values.get(
                    'character_region', {}).get('values', ['N/A'])[0]
                character_info['rarity'] = filter_values.get(
                    'character_rarity', {}).get('values', ['N/A'])[0]

                all_characters.append(character_info)

            print(
                f"Adicionados {len(current_page_entries)} personagens da página {page_num}.")

            # Condição para parar o loop: se já coletamos todos os personagens
            # ou se a página atual retornou menos itens que o page_size esperado,
            # o que geralmente indica a última página.
            if len(all_characters) >= total_entries or len(current_page_entries) < page_size:
                print(
                    "Todos os personagens foram coletados ou a última página foi atingida.")
                break

            page_num += 1
            # É uma boa prática adicionar um pequeno atraso entre as requisições
            # para não sobrecarregar o servidor da API.
            time.sleep(1)  # Espera 1 segundo entre as requisições

        else:
            print(
                "Estrutura de dados inesperada ou 'data'/'list' ausente na resposta da API.")
            print(data)  # Imprime a resposta completa para depuração
            break  # Sai do loop em caso de estrutura inesperada

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição da página {page_num}: {e}")
        break  # Sai do loop em caso de erro na requisição
    except json.JSONDecodeError:
        print(
            f"Erro ao decodificar JSON da resposta da página {page_num}. Conteúdo da resposta:\n{response.text}") # type: ignore
        break  # Sai do loop em caso de JSON inválido
    except Exception as e:
        print(
            f"Ocorreu um erro inesperado ao processar a página {page_num}: {e}")
        break  # Sai do loop para outros erros

print(
    f"\nRaspagem concluída! Total de personagens coletados: {len(all_characters)}")

# Exemplo de como visualizar os primeiros 5 personagens coletados
print("\nPrimeiros 5 personagens coletados:")
for char in all_characters[:5]:
    print(char)

# Opcional: Salvar os dados em um arquivo JSON ou CSV
# Salvando em JSON
output_json_file = "all_genshin_characters.json"
with open(output_json_file, 'w', encoding='utf-8') as f:
    json.dump(all_characters, f, indent=4, ensure_ascii=False)
print(f"\nDados salvos em '{output_json_file}'")

# Salvando em CSV (requer a biblioteca pandas)
# import pandas as pd
# df = pd.DataFrame(all_characters)
# output_csv_file = "all_genshin_characters.csv"
# df.to_csv(output_csv_file, index=False, encoding='utf-8-sig')
# print(f"Dados salvos em '{output_csv_file}'")
