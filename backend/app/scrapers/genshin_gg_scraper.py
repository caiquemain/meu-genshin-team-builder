# backend/app/scrapers/genshin_gg_scraper.py
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from typing import List, Dict, Any, Optional, Union, cast, Set

GENSHIN_GG_URL = "https://genshin.gg/tier-list/"


def scrape_genshin_gg(all_backend_characters_map: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """
    Raspa os dados da Tier List do genshin.gg.
    Retorna uma lista de dicionários com os dados padronizados.
    Recebe all_backend_characters_map para enriquecer dados.
    """
    # Não precisa de create_app ou app_context aqui, pois o orquestrador fornecerá o contexto.
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=options)

        try:
            print(f"Scraping {GENSHIN_GG_URL} (Site: genshin_gg)...")
            driver.get(GENSHIN_GG_URL)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "tierlist-dropzone"))
            )
            print("Página carregada, extraindo HTML...")

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            tier_data_raw: List[Dict[str, Any]] = []
            tier_rows: List[Tag] = cast(
                List[Tag], soup.find_all('div', class_='dropzone-row'))

            processed_character_ids: Set[str] = set()

            for row_tag in tier_rows:
                tier_title_element_raw: Optional[Union[Tag, NavigableString]] = row_tag.find(
                    'div', class_='dropzone-title') # type: ignore
                tier_title_element: Optional[Tag] = cast(
                    Tag, tier_title_element_raw) if isinstance(tier_title_element_raw, Tag) else None

                tier_level: str = tier_title_element.get_text(
                    strip=True) if tier_title_element else "Unknown Tier"

                characters_in_tier_desktop_raw: Optional[Union[Tag, NavigableString]] = row_tag.find(
                    'div', class_=['dropzone-characters'], attrs={'tier': tier_level}) # type: ignore
                characters_in_tier_mobile_raw: Optional[Union[Tag, NavigableString]] = row_tag.find(
                    'div', class_=['dropzone-characters', '--mobile'], attrs={'tier': tier_level}) # type: ignore # type: ignore

                characters_in_tier_desktop: Optional[Tag] = cast(
                    Tag, characters_in_tier_desktop_raw) if isinstance(characters_in_tier_desktop_raw, Tag) else None
                characters_in_tier_mobile: Optional[Tag] = cast(
                    Tag, characters_in_tier_mobile_raw) if isinstance(characters_in_tier_mobile_raw, Tag) else None

                all_character_portraits: List[Tag] = []
                if characters_in_tier_desktop:
                    all_character_portraits.extend(cast(
                        List[Tag], characters_in_tier_desktop.find_all('a', class_='tierlist-portrait')))
                if characters_in_tier_mobile:
                    all_character_portraits.extend(cast(
                        List[Tag], characters_in_tier_mobile.find_all('a', class_='tierlist-portrait')))

                for char_portrait_tag in all_character_portraits:
                    char_name_element: Optional[Tag] = char_portrait_tag.find(
                        'h2', class_='tierlist-name') # type: ignore
                    char_role_element: Optional[Tag] = char_portrait_tag.find(
                        'h3', class_='tierlist-role') # type: ignore
                    char_constellation_element: Optional[Tag] = char_portrait_tag.find(
                        'div', class_='tierlist-constellation') # type: ignore
                    char_rarity_class_element: Optional[Tag] = char_portrait_tag.find(
                        'img', class_='tierlist-icon') # type: ignore
                    char_element_icon_element: Optional[Tag] = char_portrait_tag.find(
                        'img', class_='tierlist-type') # type: ignore

                    char_name: str = char_name_element.get_text(
                        strip=True) if char_name_element else "Unknown"
                    char_role: str = char_role_element.get_text(
                        strip=True) if char_role_element else "Unknown Role"
                    char_constellation: Optional[str] = char_constellation_element.get_text(
                        strip=True) if char_constellation_element else "C0"

                    rarity: Optional[int] = None
                    if char_rarity_class_element:
                        rarity_classes_attr: Optional[Union[str, List[str]]] = char_rarity_class_element.get(
                            'class')
                        if isinstance(rarity_classes_attr, list) and len(rarity_classes_attr) > 1 and 'rarity-' in rarity_classes_attr[1]:
                            try:
                                rarity = int(
                                    rarity_classes_attr[1].replace('rarity-', ''))
                            except ValueError:
                                pass

                    element: Optional[str] = char_element_icon_element.get(
                        'alt', 'Unknown') if char_element_icon_element else 'Unknown' # type: ignore

                    character_id_from_site: Optional[str] = char_portrait_tag.get(
                        'characterid') # type: ignore

                    if not character_id_from_site:
                        href_val: Optional[str] = char_portrait_tag.get('href') # type: ignore
                        if href_val:
                            character_id_from_site = href_val.strip(
                                '/').split('/')[-1]
                        else:
                            character_id_from_site = char_name.lower().replace(' ', '_').replace('.', '')

                    if character_id_from_site is None:
                        print(
                            f"Aviso: character_id_from_site é None para {char_name}. Pulando este personagem.")
                        continue

                    # Não vamos mais pular duplicação aqui, o orquestrador vai lidar com isso ou adicionar todos.
                    # Mas para o teste local, o processed_character_ids garante que não tentemos adicionar na lista raw.
                    if character_id_from_site in processed_character_ids:
                        continue

                    # Cria um dicionário com os dados padronizados e adiciona a fonte
                    tier_data_raw.append({
                        "character_id": character_id_from_site,
                        "character_name": char_name,
                        "tier_level": tier_level,
                        "role": char_role,
                        "constellation": char_constellation,
                        "rarity": rarity,
                        "element": element,
                        "source_site": "genshin_gg"  # Define a fonte do site
                    })
                    # Adiciona ao set de IDs processados para unicidade interna ao scraper
                    processed_character_ids.add(character_id_from_site)

            print(f"Extraídos {len(tier_data_raw)} personagens de genshin.gg.")
            return tier_data_raw

        except Exception as e:
            # Não fazer rollback aqui, pois a transacao será gerenciada pelo orquestrador.
            print(f"Erro no WebDriver/Scraping para genshin.gg: {e}")
            return None
        finally:
            if 'driver' in locals() and driver:
                driver.quit()

    except Exception as e:
        print(
            f"Erro geral no scraper de genshin.gg (fora do contexto do driver): {e}")
        return None

# Nao ha bloco if __name__ == "__main__" aqui. O orquestrador chamará.
