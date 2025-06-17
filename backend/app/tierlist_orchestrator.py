# backend/app/tierlist_orchestrator.py
import os
import json
from typing import List, Dict, Any, Optional, Set, Union
from collections import defaultdict
import re

from app import create_app, db
from app.models import TierListEntry

from app.data_loader import get_all_characters_map, load_all_character_data, load_all_artifacts_data, load_all_weapons_data
from app.services.team_suggester import load_defined_compositions

# Importe os scrapers individuais
from app.scrapers.genshin_gg_scraper import scrape_genshin_gg, GENSHIN_GG_URL
from app.scrapers.game8_scraper import scrape_game8_co, GAME8_URL
from app.scrapers.genshinlab_scraper import scrape_genshinlab_com, GENSHINLAB_URL

TIER_LIST_JSON_OUTPUT_DIR = "scraped_tier_lists"

# --- MAPA DE ALIASES PARA CONSOLIDAR IDS DE PERSONAGENS DE SITES EXTERNOS ---
# Chave: ID ou nome (limpo/padronizado) que vem do scraper.
# Valor: SEU ID CANÔNICO (EXATO, case-sensitive) do backend.
CHARACTER_ID_ALIASES = {
    # Genshin.gg e Game8.co IDs numéricos (chave é a STRING numérica exata)
    # Estes devem mapear para os IDs CANÔNICOS do seu `character_definitions`
    "85": "arlecchino", "69": "baizhu", "97": "citlali", "78": "furina",
    # <-- Notei que seu `kazuha.json` tem ID "kaedehara_kazuha". O alias deve ser para o ID EXATO do seu JSON.
    "14": "kazuha",
    "96": "mavuika", "19": "nahida", "76": "neuvillette",
    "93": "xilonen", "33": "yelan", "35": "zhongli", "39": "bennett",
    "50": "kuki_shinobu",
    "62": "xingqiu", "02": "alhaitham", "04": "ayaka",
    # <-- Se seu childe.json tem ID "Childe", então este deve ser "Childe".
    "94": "chasca", "06": "Childe",
    "84": "chiori", "86": "clorinde", "89": "emilie", "1c": "escoffier",
    # <-- Se seu hu_tao.json tem ID "hu_tao", então este deve ser "hu_tao".
    "10": "ganyu", "11": "hu_tao",
    "92": "kinich", "17": "kokomi",
    # <-- Raiden (ID numérico -> raiden_shogun)
    "73": "lyney", "90": "mualani", "80": "navia", "22": "raiden_shogun",
    "23": "shenhe", "88": "sigewinne", "24": "tighnari", "1a": "varesa",
    # <-- Yae Miko (ID numérico -> yae_miko)
    "77": "wriothesley", "82": "xianyun", "32": "yae_miko",
    "79": "charlotte", "46": "fischl", "95": "ororon", "61": "xiangling",
    "01": "albedo", "05": "ayato", "67": "dehya", "12": "itto",
    "13": "jean", "15": "keqing", "18": "mona", "20": "nilou",
    # <-- Se seu wanderer.json tem ID "wanderer", então este deve ser "wanderer".
    "29": "venti", "30": "wanderer",
    "31": "xiao", "34": "yoimiya", "0a": "yumemizuki_mizuki",  # <-- yumemizuki_mizuki
    "38": "beidou", "81": "chevreuse", "43": "diona", "45": "faruzan",
    "47": "gorou", "2a": "iansan", "91": "kachina", "98": "lan_yan",
    "51": "layla", "56": "rosaria", "57": "kujou_sara",  # <-- Sara
    "59": "sucrose", "60": "thoma", "65": "yaoyao", "07": "cyno",
    "08": "diluc", "09": "eula", "16": "klee",  # <-- Klee
    "26": "traveler_dendro",  # <-- Traveler (Dendro)
    "99": "traveler_pyro",  # <-- Traveler (Pyro)
    "37": "barbara", "40": "candace", "41": "chongyun", "42": "collei",
    "44": "dori", "75": "freminet", "83": "gaming", "48": "heizou",  # <-- Heizou
    "1b": "ifa", "49": "kaeya", "71": "kirara", "52": "lisa",
    "72": "lynette", "68": "mika", "53": "ningguang", "54": "noelle",
    "87": "sethos", "63": "xinyan", "64": "yanfei", "66": "yun_jin",
    "03": "aloy", "21": "qiqi", "25": "traveler_anemo",  # <-- Traveler (Anemo)
    "27": "traveler_electro",  # <-- Traveler (Electro)
    "28": "traveler_geo",  # <-- Traveler (Geo)
    "74": "traveler_hydro",  # <-- Traveler (Hydro)
    "36": "amber", "70": "kaveh", "55": "razor", "58": "sayu",

    # Variações de IDs e nomes compostos de outros sites (chave é o ID/nome LIMPO/PADRONIZADO vindo do scraper)
    # Valor: SEU ID CANÔNICO (EXATO) do backend.
    # genshinlab.com "shikanoin-heizou" limpo para shikanoin_heizou
    "shikanoin_heizou": "heizou",
    # genshinlab.com "childe-tartaglia" limpo para childe_tartaglia -> Childe
    "childe_tartaglia": "Childe",
    # genshinlab.com "raiden-shogun" limpo para raiden_shogun
    "raiden_shogun": "raiden_shogun",
    "hu_tao": "hu_tao",           # GenshinLab "hu-tao" limpo para hu_tao
    "yae_miko": "yae_miko",       # GenshinLab "yae-miko" limpo para yae_miko
    "yun_jin": "yun_jin",        # GenshinLab "yun-jin" limpo para yun_jin
    "arataki_itto": "itto",      # GenshinLab "arataki_itto" limpo para itto
    # genshinlab.com "traveler-pyro" limpo para traveler_pyro
    "traveler_pyro": "traveler_pyro",
    # genshinlab.com "travelerdendro" limpo para traveler_dendro
    "travelerdendro": "traveler_dendro",
    # genshinlab.com "travelerelectro" limpo para traveler_electro
    "travelerelectro": "traveler_electro",
    # genshinlab.com "traveler-geo" limpo para traveler_geo
    "traveler_geo": "traveler_geo",
    # genshinlab.com "traveler_hydro_build" limpo para traveler_hydro
    "traveler_hydro": "traveler_hydro",
    "kuki_shinobu": "kuki_shinobu",
    "aloy": "aloy",
    "klee": "klee",
    "amber": "amber",
    # GenshinLab tem Dahlia, que não está no seu character_definitions (se este for o caso, ele sera pulado)
    "dahlia": "dahlia",
    "skirk": "skirk",
    "dahlia": "dahlia",
    "traveler_hydro_build": "traveler_hydro",
    "ifa": "ifa",  # genshinlab.com usa ifa-build limpo para ifa
    "jean": "jean",  # genshinlab.com usa jean-build limpo para jean
    "kachina": "kachina",  # genshinlab.com usa kachina-build limpo para kachina
    "lan_yan": "lan_yan",  # genshinlab.com usa lan-yan-build limpo para lan_yan
    "lynette": "lynette",  # genshinlab.com usa lynette-build limpo para lynette
    # game8.co "mizuki dps" limpo para yumemizuki_mizuki
    "yumemizuki_mizuki": "yumemizuki_mizuki",
    "yoimiya": "yoimiya",  # game8.co "yoimiya dps" limpo para yoimiya
    "sethos": "sethos",  # game8.co "sethos dps" limpo para sethos
    "itto": "itto",  # game8.co "itto dps" limpo para itto
    "cyno": "cyno",  # game8.co "cyno dps" limpo para cyno
    "eula": "eula",  # game8.co "eula dps" limpo para eula
    "diluc": "diluc",  # game8.co "diluc dps" limpo para diluc
    "wanderer": "wanderer",  # game8.co "wanderer dps" limpo para wanderer
    "ganyu": "ganyu",  # game8.co "ganyu dps" limpo para ganyu
    # game8.co "traveler (pyro) dps" limpo para traveler_pyro
    "traveler_pyro": "traveler_pyro",
    # game8.co "traveler (dendro) dps" limpo para traveler_dendro
    "traveler_dendro": "traveler_dendro",
    "kujou_sara": "kujou_sara",  # game8.co "sara dps" limpo para kujou_sara
    "heizou": "heizou",  # game8.co "heizou dps" limpo para heizou
    "klee": "klee",  # game8.co "klee dps" limpo para klee
    # game8.co "traveler (electro) dps" limpo para traveler_electro
    "traveler_electro": "traveler_electro",
    # game8.co "traveler (geo) dps" limpo para traveler_geo
    "traveler_geo": "traveler_geo",
    # game8.co "traveler (anemo) dps" limpo para traveler_anemo
    "traveler_anemo": "traveler_anemo",
    # game8.co "traveler (hydro) dps" limpo para traveler_hydro
    "traveler_hydro": "traveler_hydro",
    "aloy": "aloy",  # game8.co "aloy dps" limpo para aloy
    "razor": "razor",  # game8.co "razor dps" limpo para razor
    "xinyan": "xinyan",  # game8.co "xinyan dps" limpo para xinyan
    "yanfei": "yanfei",  # game8.co "yanfei dps" limpo para yanfei
    "kokomi": "kokomi",  # game8.co "kokomi dps" limpo para kokomi
    "freminet": "freminet",  # game8.co "freminet dps" limpo para freminet
    "ningguang": "ningguang",  # game8.co "ningguang dps" limpo para ningguang
    "gaming": "gaming",  # game8.co "gaming dps" limpo para gaming
    "mualani": "mualani",  # game8.co "mualani dps" limpo para mualani
    "kinich": "kinich",  # game8.co "kinich dps" limpo para kinich
    "navia": "navia",  # game8.co "navia dps" limpo para navia
    "arlecchino": "arlecchino",  # game8.co "arlecchino dps" limpo para arlecchino
    "clorinde": "clorinde",  # game8.co "clorinde dps" limpo para clorinde
    "ayaka": "ayaka",  # game8.co "ayaka dps" limpo para ayaka
    "xiao": "xiao",  # game8.co "xiao dps" limpo para xiao
    "ayato": "ayato",  # game8.co "ayato dps" limpo para ayato
    "tighnari": "tighnari",  # game8.co "tighnari dps" limpo para tighnari
    "chasca": "chasca",  # game8.co "chasca dps" limpo para chasca
    "emilie": "emilie",  # game8.co "emilie dps" limpo para emilie
    "chiori": "chiori",  # game8.co "chiori dps" limpo para chiori
    "ororon": "ororon",  # game8.co "ororon dps" limpo para ororon
    "337161": "raiden_shogun",
    "346199": "kuki_shinobu",
    "305862": "Childe",
    "309656": "wanderer",
    "345461": "itto",
    "470309": "traveler_pyro",
    "381807": "traveler_dendro",
    "336727": "kujou_sara",
    "345516": "heizou",
    "336865": "traveler_electro",
    "297538": "traveler_geo",
    "297537": "traveler_anemo",
    "416602": "traveler_hydro"
}


def populate_character_aliases_from_backend_data(all_backend_characters_map: Dict[str, Any]) -> None:
    """
    Popula o dicionário CHARACTER_ID_ALIASES com variações de IDs e nomes
    baseadas nos dados canônicos do backend.
    """
    # Para cada personagem no seu mapa de backend
    for canonical_id, char_data in all_backend_characters_map.items():
        canonical_name = char_data.get("name")
        if not canonical_name:
            continue

        # 1. Adicionar o próprio ID canônico (snake_case) como alias para ele mesmo
        CHARACTER_ID_ALIASES[canonical_id.lower()] = canonical_id

        # 2. Adicionar o nome canônico (limpo) como alias para o ID canônico
        # Ex: "Albedo" -> "albedo"
        cleaned_name_for_alias = canonical_name.lower().replace(' ', '_').replace(
            '.', '').replace('-', '_').replace('(', '').replace(')', '')
        CHARACTER_ID_ALIASES[cleaned_name_for_alias] = canonical_id

        # 3. Gerar variações comuns de nomes compostos ou com caracteres especiais
        # Ex: "Shogun Raiden" -> "raiden_shogun"
        if " " in canonical_name or "(" in canonical_name:
            # Tentar remover parenteses e espaços para criar um alias
            variation_id = canonical_name.lower().replace(
                ' ', '_').replace('(', '').replace(')', '')
            CHARACTER_ID_ALIASES[variation_id] = canonical_id

        # Ex: "Kujou Sara" -> "kujou_sara" ou "sara" (se Sara for um ID comum)
        if '_' in canonical_id:
            hyphenated_id = canonical_id.replace('_', '-')
            CHARACTER_ID_ALIASES[hyphenated_id] = canonical_id

            # Se o ID canônico for composto (ex: raiden_shogun), adicione o primeiro termo como um alias
            # Ex: "raiden_shogun" -> "raiden"
            first_part_id = canonical_id.split('_')[0]
            CHARACTER_ID_ALIASES[first_part_id] = canonical_id

        # Para Traveler, que tem muitas variações de nome e ID em sites
        if canonical_id.startswith("traveler_"):
            # Ex: "traveler_dendro" -> "travelerdendro" (genshinlab sem underscore)
            CHARACTER_ID_ALIASES[canonical_id.replace('_', '')] = canonical_id
            # Ex: "traveler_dendro" -> "traveler (dendro)" (genshin.gg formatado)
            # 'dendro', 'electro', etc.
            element_name = canonical_id.split('_')[1]
            CHARACTER_ID_ALIASES[f"traveler ({element_name})"] = canonical_id
            # Variacao com hifen
            CHARACTER_ID_ALIASES[f"traveler-{element_name}"] = canonical_id
            # Variacao com underscore (já é o canônico, mas garante)
            CHARACTER_ID_ALIASES[f"traveler_{element_name}"] = canonical_id


def get_canonical_id_and_name(scraped_char_id: str, scraped_char_name: str, source_site: str, all_backend_characters_map: Dict[str, Any]) -> Dict[str, str]:
    """
    Tenta encontrar o ID e nome canônicos do personagem, usando aliases e o mapa do backend.
    Prioriza o mapeamento de aliases, depois a busca direta no backend pelo ID/Nome.
    Retorna um dicionário {'id': canonical_id, 'name': canonical_name}.
    """
    # 1. Tentar mapear o ID raspado ORIGINAL (útil para IDs numéricos)
    if scraped_char_id in CHARACTER_ID_ALIASES:
        canonical_id = CHARACTER_ID_ALIASES[scraped_char_id]
        if canonical_id in all_backend_characters_map:  # Validar se o alias existe no backend map
            return {"id": canonical_id, "name": all_backend_characters_map[canonical_id]["name"]}
        # Se o alias nos levou a um ID que não está no backend map (problema de alias ou backend)
        print(
            f"Aviso: Alias '{scraped_char_id}' mapeou para ID '{canonical_id}', mas este ID NÃO está no backend map. Tentar outras lógicas.")

    # 2. Limpeza do ID raspado para padronização e lookup no alias map (string)
    cleaned_scraped_id_for_alias_lookup = scraped_char_id.lower()
    cleaned_scraped_id_for_alias_lookup = re.sub(
        r'-(best-builds|build|dps|sub-dps|support|rank|shogun|tartaglia|geo|electro|anemo|hydro|pyro)$', '', cleaned_scraped_id_for_alias_lookup).strip()
    cleaned_scraped_id_for_alias_lookup = cleaned_scraped_id_for_alias_lookup.replace(
        ' ', '_').replace('.', '').replace('-', '_').replace('(', '').replace(')', '')

    if cleaned_scraped_id_for_alias_lookup in CHARACTER_ID_ALIASES:
        canonical_id = CHARACTER_ID_ALIASES[cleaned_scraped_id_for_alias_lookup]
        if canonical_id in all_backend_characters_map:  # Validar se o alias existe no backend map
            return {"id": canonical_id, "name": all_backend_characters_map[canonical_id]["name"]}
        print(
            f"Aviso: Alias '{cleaned_scraped_id_for_alias_lookup}' mapeou para ID '{canonical_id}', mas este ID NÃO está no backend map. Tentar outras lógicas.")

    # 3. Tentar encontrar no all_backend_characters_map pelo ID raspado (já limpo e padronizado)
    # Esta é a principal tentativa para IDs como 'arlecchino', 'kazuha', 'nahida' que já são limpos.
    if cleaned_scraped_id_for_alias_lookup in all_backend_characters_map:
        return {"id": cleaned_scraped_id_for_alias_lookup, "name": all_backend_characters_map[cleaned_scraped_id_for_alias_lookup].get("name", scraped_char_name)}

    # 4. Tentar encontrar no all_backend_characters_map pelo nome raspado (limpo)
    clean_scraped_name_for_lookup = scraped_char_name.replace(" Build", "").replace(
        " DPS", "").replace(" Sub-DPS", "").replace(" Support", "").replace(" Rank", "").strip()
    clean_scraped_name_for_lookup = clean_scraped_name_for_lookup.replace(
        '(', '').replace(')', '').replace('.', '').strip()

    for backend_id, backend_char_data in all_backend_characters_map.items():
        backend_char_name = backend_char_data.get("name")
        if backend_char_name and clean_scraped_name_for_lookup.lower() == backend_char_name.lower():
            return {"id": backend_id, "name": backend_char_name}

    # 5. Se tudo falhar, usar o ID limpo e nome limpo raspados (e dar um aviso crítico)
    print(
        f"Aviso: Falha CRÍTICA ao mapear personagem '{scraped_char_name}' (ID raspado: '{scraped_char_id}', ID limpo: '{cleaned_scraped_id_for_alias_lookup}') de {source_site} para um ID canônico. Usando dados raspados limpos.")
    return {"id": cleaned_scraped_id_for_alias_lookup, "name": clean_scraped_name_for_lookup}


# Dicionário para armazenar os scores de cada personagem de cada fonte
# {'canonical_id': {'source1': score, 'source2': score}, ...}
character_scores: Dict[str, Dict[str, int]] = defaultdict(dict)

# Mapeamento do nosso sistema de tiers para números
TIER_TO_NUMERIC = {
    "SS": 5, "S": 4, "A": 3, "B": 2, "C": 1, "D": 0
}
# Mapeamento reverso para exibir
NUMERIC_TO_TIER = {
    5: "SS", 4: "S", 3: "A", 2: "B", 1: "C", 0: "D"
}

# Mapeamento para lidar com sites que tem um topo "S" mas sem "SS"
SITE_SPECIFIC_TIER_MAPPINGS = {
    "genshin_gg": {  # Genshin.gg tem S como topo, mapeia para nosso SS
        "S": 5, "A": 4, "B": 3, "C": 2, "D": 1
    },
    "game8_co": TIER_TO_NUMERIC,  # Game8.co usa SS, S, A, etc. diretamente
    # GenshinLab.com usa SS, S, A, etc. diretamente
    "genshinlab_com": TIER_TO_NUMERIC,
}


def run_all_scrapers_and_consolidate() -> Dict[str, Any]:
    print("Orquestrador: Iniciando processo de raspagem e consolidação de Tier Lists...")

    # Carregar todos os dados de personagens do backend UMA VEZ
    print("Orquestrador: Carregando dados de personagens do backend para enriquecimento dos scrapers...")
    load_all_character_data()
    load_all_artifacts_data()
    load_all_weapons_data()
    load_defined_compositions()
    all_backend_characters_map = get_all_characters_map()
    print("Orquestrador: Dados de personagens do backend carregados.")

    # NOVO: Popular os aliases dinamicamente
    print("\nOrquestrador: Populando aliases de personagens com base nos dados do backend...")
    populate_character_aliases_from_backend_data(all_backend_characters_map)
    print("Orquestrador: Aliases populados.")

    # Limpar o banco de dados da Tier List antes de raspar TUDO de novo
    print("\nOrquestrador: Limpando a tabela TierListEntry no banco de dados...")
    db.session.query(TierListEntry).delete()
    db.session.commit()
    print("Orquestrador: Tabela TierListEntry limpa.")

    all_scraped_data_raw: List[Dict[str, Any]] = []

    # --- Chamar cada scraper individualmente ---
    scrapers_to_run = [
        {"site_name": "genshin_gg", "url": GENSHIN_GG_URL,
            "scraper_func": scrape_genshin_gg},
        {"site_name": "game8_co", "url": GAME8_URL,
            "scraper_func": scrape_game8_co},
        {"site_name": "genshinlab_com", "url": GENSHINLAB_URL,
            "scraper_func": scrape_genshinlab_com},
    ]

    for scraper_info in scrapers_to_run:
        site_name = scraper_info["site_name"]
        site_url = scraper_info["url"]
        scraper_func = scraper_info["scraper_func"]

        print(f"\nOrquestrador: Iniciando raspagem para {site_name}...")
        scraped_data_from_site = scraper_func(all_backend_characters_map)

        if scraped_data_from_site:
            print(
                f"Orquestrador: Raspagem de {site_name} concluída. {len(scraped_data_from_site)} itens extraídos.")
            all_scraped_data_raw.extend(scraped_data_from_site)
        else:
            print(
                f"Orquestrador: Falha ou nenhum dado extraído de {site_name}.")

    print(
        f"\nOrquestrador: Raspagem de todos os sites concluída. Total de itens brutos extraídos: {len(all_scraped_data_raw)}.")

    # --- Salvar todos os dados brutos de todos os sites em um único JSON (para debug) ---
    if not os.path.exists(TIER_LIST_JSON_OUTPUT_DIR):
        os.makedirs(TIER_LIST_JSON_OUTPUT_DIR)

    consolidated_raw_output_path = os.path.join(
        TIER_LIST_JSON_OUTPUT_DIR, "all_scraped_raw_data.json")
    with open(consolidated_raw_output_path, 'w', encoding='utf-8') as f:
        json.dump(all_scraped_data_raw, f, indent=4, ensure_ascii=False)
    print(
        f"Orquestrador: Todos os dados brutos consolidados salvos em {consolidated_raw_output_path}")

    # --- Lógica de CONSOLIDAÇÃO e MÉDIA FINAL ---
    final_consolidated_tier_list: List[Dict[str, Any]] = []

    consolidated_characters_processing: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"total_score": 0, "source_count": 0, "roles": set(
        ), "elements": set(), "rarities": set(), "tiers_by_source": {}}
    )

    for char_data_raw in all_scraped_data_raw:
        scraped_char_id = char_data_raw['character_id']
        scraped_char_name = char_data_raw['character_name']
        tier_level_from_site = char_data_raw['tier_level']
        source_site = char_data_raw['source_site']

        # 1. Obter ID e Nome Canônicos
        canonical_info = get_canonical_id_and_name(
            scraped_char_id, scraped_char_name, source_site, all_backend_characters_map)

        # Validar se o canonical_info é valido e se o ID canonico existe no backend_characters_map
        if canonical_info["id"] not in all_backend_characters_map:
            print(
                f"Aviso: Personagem '{scraped_char_name}' (ID raspado: '{scraped_char_id}') de {source_site} NÃO possui ID canônico reconhecido no backend map. Pulando na consolidação final.")
            continue  # Pular personagens que nao conseguimos mapear para um ID canônico conhecido

        canonical_id = canonical_info['id']

        # Obter o score numérico do tier para a média
        numeric_score = SITE_SPECIFIC_TIER_MAPPINGS.get(
            source_site, TIER_TO_NUMERIC).get(tier_level_from_site, 0)

        # Atualizar dados consolidados
        consolidated_entry = consolidated_characters_processing[canonical_id]
        consolidated_entry["total_score"] += numeric_score
        consolidated_entry["source_count"] += 1
        consolidated_entry["tiers_by_source"][source_site] = tier_level_from_site

        # Adicionar roles, elements, rarities a sets para pegar unicos
        raw_role = char_data_raw.get('role')
        if raw_role:
            if isinstance(raw_role, list):  # Se for lista
                for r_item in raw_role:
                    if isinstance(r_item, str) and r_item.strip() and r_item.strip() != "Unknown Role":
                        consolidated_entry["roles"].add(r_item.strip())
            elif isinstance(raw_role, str) and raw_role.strip() and raw_role.strip() != "Unknown Role":  # Se for string
                consolidated_entry["roles"].add(raw_role.strip())

        raw_element = char_data_raw.get('element')
        if raw_element:
            if isinstance(raw_element, list):
                for e_item in raw_element:
                    if isinstance(e_item, str) and e_item.strip() and e_item.strip() != "Unknown":
                        consolidated_entry["elements"].add(e_item.strip())
            elif isinstance(raw_element, str) and raw_element.strip() and raw_element.strip() != "Unknown":
                consolidated_entry["elements"].add(raw_element.strip())

        raw_rarity = char_data_raw.get('rarity')
        if raw_rarity is not None:
            if isinstance(raw_rarity, (int, float)):
                consolidated_entry["rarities"].add(int(raw_rarity))

    # Iterar sobre os dados consolidados para calcular as medias finais
    for canonical_id, data_agg in consolidated_characters_processing.items():
        if data_agg["source_count"] == 0:
            continue

        average_numeric_tier = data_agg["total_score"] / \
            data_agg["source_count"]

        # Mapear de volta para o tier final
        final_tier_level: str
        if average_numeric_tier >= 4.5:
            final_tier_level = "SS"
        elif average_numeric_tier >= 3.5:
            final_tier_level = "S"
        elif average_numeric_tier >= 2.5:
            final_tier_level = "A"
        elif average_numeric_tier >= 1.5:
            final_tier_level = "B"
        elif average_numeric_tier >= 0.5:
            final_tier_level = "C"
        else:
            final_tier_level = "D"

        # Recuperar dados do personagem do backend para o nome principal e fallback para element/rarity/role
        backend_char_info = all_backend_characters_map.get(canonical_id)
        final_char_name = backend_char_info.get(
            "name", canonical_id) if backend_char_info else canonical_id

        # --- CORREÇÃO FINAL PARA ROLE: Definir a role FINAL priorizando o backend e forçando STRING ---
        final_role_display: str = "Unknown Role"
        if backend_char_info and "role" in backend_char_info:
            backend_role_from_map = backend_char_info["role"]
            if isinstance(backend_role_from_map, list):
                final_role_display = ", ".join(sorted(backend_role_from_map))
            elif isinstance(backend_role_from_map, str) and backend_role_from_map.strip():
                final_role_display = backend_role_from_map.strip()
        # Se não houver no backend, usar o que foi raspado (já limpo no set)
        elif data_agg["roles"]:
            final_role_display = ", ".join(sorted(list(data_agg["roles"])))

        final_rarity_display: Optional[int] = None
        if backend_char_info and "rarity" in backend_char_info:  # Priorizar raridade do backend
            final_rarity_display = backend_char_info["rarity"]
        elif data_agg["rarities"]:  # Caso contrario, usar a raspada
            final_rarity_display = max(data_agg["rarities"])

        final_element_display: str = "Unknown"
        if backend_char_info and "element" in backend_char_info:  # Priorizar elemento do backend
            final_element_display = backend_char_info["element"]
        elif data_agg["elements"]:  # Caso contrario, usar o raspado
            final_element_display = ", ".join(
                sorted(list(data_agg["elements"])))

        final_consolidated_tier_list.append({
            "character_id": canonical_id,
            "character_name": final_char_name,
            "tier_level": final_tier_level,
            "role": final_role_display,
            "constellation": "C0",
            "rarity": final_rarity_display,
            "element": final_element_display,
            "average_numeric_tier": round(average_numeric_tier, 2),
            "sources_contributing": data_agg["source_count"],
            "original_scores_by_site": data_agg["tiers_by_source"]
        })

    final_consolidated_output_path = os.path.join(
        TIER_LIST_JSON_OUTPUT_DIR, "consolidated_tier_list.json")
    with open(final_consolidated_output_path, 'w', encoding='utf-8') as f:
        json.dump(final_consolidated_tier_list,
                  f, indent=4, ensure_ascii=False)
    print(
        f"Orquestrador: Tier list consolidada salva em {final_consolidated_output_path}")

    print("\nOrquestrador: Limpando a tabela TierListEntry para inserir dados consolidados...")
    db.session.query(TierListEntry).delete()
    for entry_data in final_consolidated_tier_list:
        entry = TierListEntry(
            character_id=entry_data["character_id"],
            character_name=entry_data["character_name"],
            tier_level=entry_data["tier_level"],
            role=entry_data["role"],  # JÁ É STRING
            constellation=entry_data.get("constellation", "C0"),
            rarity=entry_data["rarity"],
            element=entry_data["element"]  # JÁ É STRING
        )
        db.session.add(entry)
    db.session.commit()
    print(
        f"Orquestrador: {len(final_consolidated_tier_list)} itens consolidados salvos na tabela TierListEntry.")

    print("\nOrquestrador: Processo de consolidação e salvamento de dados brutos concluído.")
    return {"status": "success", "message": "Tier lists raspadas e dados brutos consolidados."}


if __name__ == "__main__":
    from app import create_app

    print("\n--- INICIANDO ORQUESTRADOR MANUALMENTE ---")
    app = create_app(enable_csrf=False)
    with app.app_context():
        run_all_scrapers_and_consolidate()
