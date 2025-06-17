# backend/app/scrapers/genshinlab_scraper.py
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

from app.data_loader import get_all_characters_map

GENSHINLAB_URL = "https://genshinlab.com/tier-list/"


def scrape_genshinlab_com(all_backend_characters_map: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=options)

        try:
            print(f"Scraping {GENSHINLAB_URL} (Site: genshinlab_com)...")
            driver.get(GENSHINLAB_URL)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.elementor-posts-container"))
            )
            print("Página carregada, extraindo HTML...")

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            tier_list_data: List[Dict[str, Any]] = []
            processed_character_ids: Set[str] = set()

            tier_sections: List[Tag] = cast(List[Tag], soup.find_all(
                'section', class_=lambda val: val and 'elementor-inner-section' in val and 'elementor-section-boxed' in val))  # type: ignore

            for section_tag in tier_sections:
                tier_level_header_raw: Optional[Union[Tag, NavigableString]] = section_tag.find(
                    # type: ignore # type: ignore
                    'h6', style=lambda value: value and 'text-align: center' in value) # type: ignore
                tier_level_span: Optional[Tag] = cast(Tag, tier_level_header_raw).find(
                    # type: ignore
                    'span') if isinstance(tier_level_header_raw, Tag) else None

                tier_level: str = tier_level_span.get_text(
                    strip=True) if tier_level_span else "Unknown Tier"
                tier_level = tier_level.replace(" Tier", "").strip()

                if tier_level in ["Unknown Tier", "Best Characters", "All Characters", "Filter by", "Genshin Impact Tier List"]:
                    continue

                characters_container: Optional[Tag] = section_tag.find(
                    'div', class_=lambda val: val and 'elementor-posts-container' in val)  # type: ignore

                if characters_container:
                    character_articles: List[Tag] = cast(
                        List[Tag], characters_container.find_all('article', class_='elementor-post'))

                    for char_article_tag in character_articles:
                        char_name_link_raw: Optional[Union[Tag, NavigableString]] = char_article_tag.find(
                            'h3', class_='elementor-post__title')  # type: ignore
                        char_name_link: Optional[Tag] = cast(Tag, char_name_link_raw).find(
                            # type: ignore
                            'a') if isinstance(char_name_link_raw, Tag) else None

                        char_name_full: str = char_name_link.get_text(
                            strip=True) if char_name_link else "Unknown"
                        char_name: str = char_name_full.replace(
                            " Build", "").strip()  # Limpa " Build" do nome

                        href_val: Optional[str] = char_name_link.get(
                            'href') if char_name_link else None  # type: ignore
                        character_id_from_site: Optional[str] = None
                        if href_val:
                            segments = [s for s in href_val.strip(
                                '/').split('/') if s]
                            if segments:
                                # CORREÇÃO AQUI: Remover "-build" do ID extraído da URL
                                character_id_from_site = segments[-1].lower().replace(
                                    '-build', '')

                        if not character_id_from_site:
                            character_id_from_site = char_name.lower().replace(
                                ' ', '_').replace('.', '').replace('-', '_')

                        rarity: Optional[int] = None
                        article_classes: List[str] = char_article_tag.get(
                            'class', [])  # type: ignore
                        for cls in article_classes:
                            if cls.startswith('rarity-rarity-'):
                                try:
                                    rarity = int(cls.replace(
                                        'rarity-rarity-', ''))
                                    break
                                except ValueError:
                                    pass

                        constellation: str = "C0"

                        # Papel/Role e Elemento: Inicializar e enriquecer do nosso backend
                        role: str = "Unknown Role"  # Valor padrao inicial
                        element: str = "Unknown"  # Valor padrao inicial

                        backend_char_data = all_backend_characters_map.get(
                            character_id_from_site)
                        if backend_char_data:
                            # CORREÇÃO AQUI: Priorizar o role do backend, se disponivel e nao for lista/desconhecido no site
                            if isinstance(backend_char_data.get('role'), str) and backend_char_data.get('role') != 'Unknown Role':
                                # Prioriza role do backend se for string
                                role = backend_char_data.get('role')

                            element = backend_char_data.get('element', element)
                            rarity = backend_char_data.get('rarity', rarity)

                        # Se a role do site for uma lista (como nos exemplos), precisamos lidar com ela.
                        # Nao extraimos a role do HTML do GenshinLab diretamente, entao ela sera Unknown Role
                        # ou sera do backend_char_data.

                        # Limpar character_name final
                        # Remover qualquer indicacao de role que possa ter vindo de alt text ou similares
                        # Embora ja limpamos " Build", podemos ter "DPS", "Support" etc.
                        char_name = char_name.replace(' DPS', '').replace(
                            ' Sub-DPS', '').replace(' Support', '').strip()

                        if character_id_from_site is None:
                            print(
                                f"Aviso: character_id_from_site é None para {char_name}. Pulando este personagem.")
                            continue

                        if character_id_from_site in processed_character_ids:
                            print(
                                f"Aviso: Personagem '{char_name}' (ID: {character_id_from_site}) de genshinlab.com já foi adicionado. Pulando duplicação.")
                            continue

                        tier_list_data.append({
                            "character_id": character_id_from_site,
                            "character_name": char_name,
                            "tier_level": tier_level,
                            "role": role,  # Agora sera single string do backend ou Unknown
                            "constellation": constellation,
                            "rarity": rarity,
                            "element": element,
                            "source_site": "genshinlab_com"
                        })
                        processed_character_ids.add(character_id_from_site)

            print(
                f"Extraídos {len(tier_list_data)} personagens de genshinlab.com.")
            return tier_list_data

        except Exception as e:
            print(f"Erro no WebDriver/Scraping para genshinlab.com: {e}")
            return None
        finally:
            if 'driver' in locals() and driver:
                driver.quit()

    except Exception as e:
        print(f"Erro geral no scraper de genshinlab.com: {e}")
        return None
