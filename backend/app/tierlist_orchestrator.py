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

from app.scrapers.genshin_gg_scraper import scrape_genshin_gg, GENSHIN_GG_URL
from app.scrapers.game8_scraper import scrape_game8_co, GAME8_URL
from app.scrapers.genshinlab_scraper import scrape_genshinlab_com, GENSHINLAB_URL

TIER_LIST_JSON_OUTPUT_DIR = "scraped_tier_lists"

# --- MAPA DE ALIASES PARA CONSOLIDAR IDS DE PERSONAGENS DE SITES EXTERNOS ---
# Chave: ID ou nome (limpo/padronizado) que vem do scraper.
# Valor: SEU ID CANÔNICO (EXATO, case-sensitive) do backend.
CHARACTER_ID_ALIASES: Dict[str, str] = {
    # Mapeamentos explícitos para IDs numéricos de Genshin.gg e Game8.co
    # Que o populate_character_aliases_from_backend_data não consegue gerar.
    # Baseado no log de erros:
    "14": "kazuha",  # Kazuha
    "06": "childe",  # childe (ID capitalizado no JSON)
    "11": "hu_tao",  # Hu Tao
    "12": "itto",
    "22": "raiden_shogun",  # Raiden
    "30": "wanderer",
    "32": "yae_miko",  # Yae Miko
    "57": "kujou_sara",  # Sara
    "16": "klee",  # Klee
    "99": "traveler_pyro",  # Traveler (Pyro)
    "26": "traveler_dendro",  # Traveler (Dendro)
    "25": "traveler_anemo",  # Traveler (Anemo)
    "27": "traveler_electro",  # Traveler (Electro)
    "28": "traveler_geo",  # Traveler (Geo)
    "74": "traveler_hydro",  # Traveler (Hydro)
    "48": "heizou",  # Heizou
    "0a": "yumemizuki_mizuki",  # Yumemizuki Mizuki (ID alfanumérico)

    # IDs de Game8.co (numéricos que vêm com sufixo DPS ou outros)
    "333140": "skirk",  # "Skirk DPS"
    "337161": "raiden_shogun",  # "Raiden DPS", "Raiden"
    "346199": "kuki_shinobu",  # "Shinobu"
    "305862": "childe",  # "Tartaglia DPS"
    "309656": "wanderer",  # "Wanderer DPS"
    "345461": "itto",  # "Itto DPS"
    "470309": "traveler_pyro",  # "Traveler (Pyro)"
    "381807": "traveler_dendro",  # "Traveler (Dendro)"
    "336727": "kujou_sara",  # "Sara"
    "345516": "heizou",  # "Heizou DPS"
    "297521": "klee",  # "Klee DPS"
    "336865": "traveler_electro",  # "Traveler (Electro)"
    "297538": "traveler_geo",  # "Traveler (Geo)"
    "297537": "traveler_anemo",  # "Traveler (Anemo)"
    "416602": "traveler_hydro",  # "Traveler (Hydro)"
    "516026": "dahlia",  # "Dahlia" (ID numérico)


    # Variações de IDs e nomes compostos de outros sites (chave é o ID/nome LIMPO/PADRONIZADO vindo do scraper)
    # Valor: SEU ID CANÔNICO (EXATO) do backend.
    "shikanoin_heizou": "heizou",
    "childe_tartaglia": "childe",
    # Confirma a chave como raiden_shogun, valor raiden_shogun
    "raiden_shogun": "raiden_shogun",
    "hu_tao": "hu_tao",
    "yae_miko": "yae_miko",
    "yun_jin": "yun_jin",
    "arataki_itto": "itto",
    "traveler_pyro": "traveler_pyro",
    "travelerdendro": "traveler_dendro",
    "travelerelectro": "traveler_electro",
    "traveler_geo": "traveler_geo",
    "traveler_hydro": "traveler_hydro",
    "kuki_shinobu": "kuki_shinobu",
    "aloy": "aloy",
    "klee": "klee",
    "amber": "amber",
    "dahlia": "dahlia",  # Verifique se `dahlia.json` existe com ID "dahlia"
    "ifa": "ifa",
    "jean": "jean",
    "kachina": "kachina",
    "lan_yan": "lan_yan",
    "lynette": "lynette",
    "yumemizuki_mizuki": "yumemizuki_mizuki",
    "yoimiya": "yoimiya",
    "sethos": "sethos",
    "itto": "itto",
    "cyno": "cyno",
    "eula": "eula",
    "diluc": "diluc",
    "wanderer": "wanderer",
    "ganyu": "ganyu",
    "kujou_sara": "kujou_sara",
    "heizou": "heizou",
    "traveler_anemo": "traveler_anemo",
    "traveler_electro": "traveler_electro",
    "traveler_geo": "traveler_geo",
    "traveler_hydro": "traveler_hydro",
    "razor": "razor",
    "xinyan": "xinyan",
    "yanfei": "yanfei",
    "kokomi": "kokomi",
    "freminet": "freminet",
    "ningguang": "ningguang",
    "gaming": "gaming",
    "mualani": "mualani",
    "kinich": "kinich",
    "navia": "navia",
    "arlecchino": "arlecchino",
    "clorinde": "clorinde",
    "ayaka": "ayaka",
    "xiao": "xiao",
    "ayato": "ayato",
    "tighnari": "tighnari",
    "chasca": "chasca",
    "emilie": "emilie",
    "chiori": "chiori",
    "ororon": "ororon",
    "xiangling": "xiangling",
    "xingqiu": "xingqiu",
    "albedo": "albedo",
    "alhaitham": "alhaitham",
    "baizhu": "baizhu",
    "barbara": "barbara",
    "beidou": "beidou",
    "bennett": "bennett",
    "candace": "candace",
    "charlotte": "charlotte",
    "chevreuse": "chevreuse",
    # Alias para "childe" (se houver um childe.json com ID "childe" minusculo)
    "childe": "childe",
    "chongyun": "chongyun",
    "citlali": "citlali",
    "collei": "collei",
    "dehya": "dehya",
    "diona": "diona",
    "dori": "dori",
    "escoffier": "escoffier",
    "faruzan": "faruzan",
    "fischl": "fischl",
    "furina": "furina",
    "gorou": "gorou",
    "lisa": "lisa",
    "lynette": "lynette",
    "mika": "mika",
    "mona": "mona",
    "nilou": "nilou",
    "qiqi": "qiqi",
    "shenhe": "shenhe",
    "sigewinne": "sigewinne",
    "skirk": "skirk",
    "traveler_hydro_build": "traveler_hydro"
}


def populate_character_aliases_from_backend_data(all_backend_characters_map: Dict[str, Any]) -> None:
    """
    Popula o dicionário CHARACTER_ID_ALIASES com variações de IDs e nomes
    baseadas nos dados canônicos do backend.
    """
    for canonical_id, char_data in all_backend_characters_map.items():
        canonical_name = char_data.get("name")
        if not canonical_name:
            continue

        # 1. Adicionar o próprio ID canônico como alias para ele mesmo (útil para lookup)
        # Garante que o ID exato do JSON do backend esteja no alias map.
        # Isso cobre IDs como "albedo", "raiden_shogun", "childe" (se o ID for maiúsculo no JSON)
        CHARACTER_ID_ALIASES[canonical_id] = canonical_id

        # 2. Adicionar o nome canônico (limpo) como alias para o ID canônico
        # Ex: "Albedo" -> "albedo"
        cleaned_name_for_alias = canonical_name.lower().replace(' ', '_').replace(
            '.', '').replace('-', '_').replace('(', '').replace(')', '')
        CHARACTER_ID_ALIASES[cleaned_name_for_alias] = canonical_id

        # 3. Gerar variações comuns de IDs/nomes compostos ou com caracteres especiais
        # Inclui hifen no nome canonico
        if " " in canonical_name or "(" in canonical_name or "-" in canonical_name:
            # Tentar remover parenteses e espaços para criar um alias
            # Ex: "Shogun Raiden" -> "shogun_raiden"
            # Ex: "childe(Tartaglia)" -> "childe_tartaglia"
            # Ex: "Hu-Tao" -> "hu_tao"
            variation_id = canonical_name.lower().replace(' ', '_').replace(
                '(', '').replace(')', '').replace('-', '_')
            CHARACTER_ID_ALIASES[variation_id] = canonical_id

        # Para IDs canônicos que já usam underscore, adicionar variações com hífens e a primeira parte do nome
        # Ex: "raiden_shogun" -> "raiden-shogun", "raiden"
        if '_' in canonical_id:
            hyphenated_id = canonical_id.replace('_', '-')
            CHARACTER_ID_ALIASES[hyphenated_id] = canonical_id

            first_part_id = canonical_id.split('_')[0]
            # Ex: "raiden" -> "raiden_shogun"
            CHARACTER_ID_ALIASES[first_part_id] = canonical_id

        # Para IDs canônicos que são a primeira parte de um nome composto
        # Ex: "kuki_shinobu" -> "kuki"
        if '_' in canonical_id and canonical_id.split('_')[0] not in CHARACTER_ID_ALIASES:
            CHARACTER_ID_ALIASES[canonical_id.split('_')[0]] = canonical_id

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
            # Add alias for just "traveler" if it exists in data or might be used by a scraper
            # Isso pode causar colisão se tiver mais de um Traveler sem especificar elemento. Melhor ser mais específico.
            CHARACTER_ID_ALIASES["traveler"] = canonical_id

    # DEBUG: Imprimir o mapa final de aliases populados
    print("DEBUG: Character ID Aliases final:")
    # Ordenar por chave para facilitar a leitura no log
    for k in sorted(CHARACTER_ID_ALIASES.keys()):
        print(f"  '{k}' -> '{CHARACTER_ID_ALIASES[k]}'")


def get_canonical_id_and_name(scraped_char_id: str, scraped_char_name: str, source_site: str, all_backend_characters_map: Dict[str, Any]) -> Dict[str, str]:
    """
    Tenta encontrar o ID e nome canônicos do personagem, usando aliases e o mapa do backend.
    Prioriza o mapeamento de aliases, depois a busca direta no backend pelo ID/Nome.
    Retorna um dicionário {'id': canonical_id, 'name': canonical_name}.
    """
    # 1. Tentar mapear o ID raspado ORIGINAL (útil para IDs numéricos)
    # Verifica diretamente se o ID original do scraper é uma chave no nosso mapa de aliases.
    if scraped_char_id in CHARACTER_ID_ALIASES:
        canonical_id_from_alias = CHARACTER_ID_ALIASES[scraped_char_id]
        # Valida se o ID canônico do alias existe no backend map
        if canonical_id_from_alias in all_backend_characters_map:
            return {"id": canonical_id_from_alias, "name": all_backend_characters_map[canonical_id_from_alias]["name"]}
        print(
            f"Aviso: Alias '{scraped_char_id}' mapeou para ID '{canonical_id_from_alias}', mas este ID NÃO está no backend map. Tentar outras lógicas.")

    # 2. Limpeza do ID raspado para padronização (snake_case) e lookup em aliases de string
    cleaned_scraped_id_for_alias_lookup = scraped_char_id.lower()
    # Remove sufixos comuns e caracteres especiais para padronizar o ID para lookup no alias map
    cleaned_scraped_id_for_alias_lookup = re.sub(
        r'-(best-builds|build|dps|sub-dps|support|rank|shogun|tartaglia|geo|electro|anemo|hydro|pyro)$', '', cleaned_scraped_id_for_alias_lookup).strip()
    cleaned_scraped_id_for_alias_lookup = cleaned_scraped_id_for_alias_lookup.replace(
        ' ', '_').replace('.', '').replace('-', '_').replace('(', '').replace(')', '')

    # Tenta com o ID raspado LIMPO no mapa de aliases de string
    if cleaned_scraped_id_for_alias_lookup in CHARACTER_ID_ALIASES:
        canonical_id = CHARACTER_ID_ALIASES[cleaned_scraped_id_for_alias_lookup]
        if canonical_id in all_backend_characters_map:
            return {"id": canonical_id, "name": all_backend_characters_map[canonical_id]["name"]}
        print(
            f"Aviso: Alias '{cleaned_scraped_id_for_alias_lookup}' mapeou para ID '{canonical_id}', mas este ID NÃO está no backend map. Tentar outras lógicas.")

    # 3. Tentar encontrar no all_backend_characters_map pelo ID raspado (já limpo e padronizado)
    # Esta é uma tentativa direta para IDs que já são canônicos ou quase.
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


def run_all_scrapers_and_consolidate() -> Dict[str, Any]: # type: ignore
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
            continue

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
            if isinstance(raw_role, list):
                for r_item in raw_role:
                    if isinstance(r_item, str) and r_item.strip() and r_item.strip() != "Unknown Role":
                        consolidated_entry["roles"].add(r_item.strip())
            elif isinstance(raw_role, str) and raw_role.strip() and raw_role.strip() != "Unknown Role":
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
            role=entry_data["role"],
            constellation=entry_data.get("constellation", "C0"),
            rarity=entry_data["rarity"],
            element=entry_data["element"],
            average_numeric_tier=entry_data["average_numeric_tier"],
            sources_contributing=entry_data["sources_contributing"],
            original_scores_by_site=entry_data["original_scores_by_site"]
        )
        db.session.add(entry)
    db.session.commit()
    print(
        f"Orquestrador: {len(final_consolidated_tier_list)} itens consolidados salvos na tabela TierListEntry.")


if __name__ == "__main__":
    from app import create_app

    print("\n--- INICIANDO ORQUESTRADOR MANUALMENTE ---")
    app = create_app(enable_csrf=False)
    with app.app_context():
        run_all_scrapers_and_consolidate()
