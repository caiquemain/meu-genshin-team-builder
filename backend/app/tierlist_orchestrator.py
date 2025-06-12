# backend/app/tierlist_orchestrator.py
import os
import json
from typing import List, Dict, Any, Optional

from app import create_app, db
from app.models import TierListEntry
from app.data_loader import get_all_characters_map, load_all_character_data, load_all_artifacts_data, load_all_weapons_data
from app.services.team_suggester import load_defined_compositions

# Importe os scrapers individuais
from app.scrapers.genshin_gg_scraper import scrape_genshin_gg
from app.scrapers.game8_scraper import scrape_game8_co
from app.scrapers.genshinlab_scraper import scrape_genshinlab_com # <-- NOVO: Importe o scraper de GenshinLab
# Outros scrapers virao aqui

TIER_LIST_JSON_OUTPUT_DIR = "scraped_tier_lists"

def run_all_scrapers_and_consolidate() -> Dict[str, Any]:
    print("Orquestrador: Iniciando processo de raspagem e consolidação de Tier Lists...")

    print("Orquestrador: Carregando dados de personagens do backend para enriquecimento dos scrapers...")
    load_all_character_data()
    load_all_artifacts_data()
    load_all_weapons_data()
    load_defined_compositions()
    all_backend_characters_map = get_all_characters_map()
    print("Orquestrador: Dados de personagens do backend carregados.")

    print("\nOrquestrador: Limpando a tabela TierListEntry no banco de dados...")
    db.session.query(TierListEntry).delete()
    db.session.commit()
    print("Orquestrador: Tabela TierListEntry limpa.")

    all_scraped_data_raw: List[Dict[str, Any]] = []
    
    # --- Chamar cada scraper individualmente ---
    scrapers_to_run = [
        {"site_name": "genshin_gg", "url": "https://genshin.gg/tier-list/", "scraper_func": scrape_genshin_gg},
        {"site_name": "game8_co", "url": "https://game8.co/games/Genshin-Impact/archives/297465", "scraper_func": scrape_game8_co},
        {"site_name": "genshinlab_com", "url": "https://genshinlab.com/tier-list/", "scraper_func": scrape_genshinlab_com}, # <-- NOVO: Adicione o scraper de GenshinLab
        # Adicione outros scrapers aqui quando estiverem prontos
    ]

    for scraper_info in scrapers_to_run:
        site_name = scraper_info["site_name"]
        site_url = scraper_info["url"]
        scraper_func = scraper_info["scraper_func"]

        print(f"\nOrquestrador: Iniciando raspagem para {site_name}...")
        scraped_data_from_site = scraper_func(all_backend_characters_map)
        
        if scraped_data_from_site:
            print(f"Orquestrador: Raspagem de {site_name} concluída. {len(scraped_data_from_site)} itens extraídos.")
            all_scraped_data_raw.extend(scraped_data_from_site)
        else:
            print(f"Orquestrador: Falha ou nenhum dado extraído de {site_name}.")

    print(f"\nOrquestrador: Raspagem de todos os sites concluída. Total de itens brutos extraídos: {len(all_scraped_data_raw)}.")

    # --- Salvar todos os dados brutos de todos os sites em um único JSON (para debug) ---
    if not os.path.exists(TIER_LIST_JSON_OUTPUT_DIR):
        os.makedirs(TIER_LIST_JSON_OUTPUT_DIR)
    
    consolidated_raw_output_path = os.path.join(TIER_LIST_JSON_OUTPUT_DIR, "all_scraped_raw_data.json")
    with open(consolidated_raw_output_path, 'w', encoding='utf-8') as f:
        json.dump(all_scraped_data_raw, f, indent=4, ensure_ascii=False)
    print(f"Orquestrador: Todos os dados brutos consolidados salvos em {consolidated_raw_output_path}")

    # --- Lógica de Consolidação e Média (A SER IMPLEMENTADA) ---
    print("\nOrquestrador: Processo de consolidação e salvamento de dados brutos concluído.")
    return {"status": "success", "message": "Tier lists raspadas e dados brutos consolidados."}

if __name__ == "__main__":
    from app import create_app

    print("\n--- INICIANDO ORQUESTRADOR MANUALMENTE ---")
    app = create_app(enable_csrf=False)
    with app.app_context():
        run_all_scrapers_and_consolidate()