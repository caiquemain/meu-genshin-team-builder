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

# Importar o mapa de personagens
from app.data_loader import get_all_characters_map

GENSHINLAB_URL = "https://genshinlab.com/tier-list/"


def scrape_genshinlab_com(all_backend_characters_map: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """
    Raspa os dados da Tier List do genshinlab.com.
    Usa Selenium. Retorna uma lista de dicionários com os dados padronizados.
    Recebe all_backend_characters_map para enriquecer dados.
    """
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

            # Esperar por um elemento que contenha a tier list principal
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.elementor-column.elementor-col-50.elementor-inner-column"))
            )
            print("Página carregada, extraindo HTML...")

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            tier_list_data: List[Dict[str, Any]] = []
            processed_character_ids: Set[str] = set()

            # Encontrar todas as seções de Tier (SS, S, A, etc.)
            # Cada seção tem um h6 com o texto do tier
            tier_sections = soup.find_all(
                'section', class_='elementor-inner-section')

            for section_tag in tier_sections:
                tier_level_header_raw: Optional[Union[Tag, NavigableString]] = section_tag.find(
                    'h6', style=lambda value: value and 'text-align: center' in value)
                tier_level_span: Optional[Tag] = cast(Tag, tier_level_header_raw).find(
                    'span') if isinstance(tier_level_header_raw, Tag) else None

                tier_level: str = tier_level_span.get_text(
                    strip=True) if tier_level_span else "Unknown Tier"
                tier_level = tier_level.replace(
                    " Tier", "").strip()  # Limpa " Tier" se presente

                # Encontrar o container de posts (personagens) para este tier
                characters_container: Optional[Tag] = section_tag.find(
                    'div', class_=lambda value: value and 'elementor-posts-container' in value)

                if characters_container:
                    # Cada personagem é uma 'article' com classe 'elementor-post elementor-grid-item'
                    character_articles: List[Tag] = cast(
                        List[Tag], characters_container.find_all('article', class_='elementor-post'))

                    for char_article_tag in character_articles:
                        char_name_link_raw: Optional[Union[Tag, NavigableString]] = char_article_tag.find(
                            'h3', class_='elementor-post__title')
                        char_name_link: Optional[Tag] = cast(Tag, char_name_link_raw).find(
                            'a') if isinstance(char_name_link_raw, Tag) else None

                        char_name: str = char_name_link.get_text(strip=True).replace(
                            " Build", "") if char_name_link else "Unknown"

                        # Extrair o ID do personagem do href (ex: /characters/arlecchino/ -> arlecchino)
                        href_val: Optional[str] = char_name_link.get(
                            'href') if char_name_link else None
                        character_id_from_site: Optional[str] = None
                        if href_val:
                            segments = [s for s in href_val.strip(
                                '/').split('/') if s]
                            if segments:
                                # Pega o último segmento (ID)
                                character_id_from_site = segments[-1].lower()

                        if not character_id_from_site:
                            character_id_from_site = char_name.lower().replace(' ', '_').replace('.', '')

                        # Extrair raridade da classe da article (ex: rarity-rarity-5)
                        rarity: Optional[int] = None
                        article_classes: List[str] = char_article_tag.get(
                            'class', [])
                        for cls in article_classes:
                            if 'rarity-rarity-' in cls:
                                try:
                                    rarity = int(cls.replace(
                                        'rarity-rarity-', ''))
                                    break
                                except ValueError:
                                    pass

                        # Extrair constelação (não explicitamente visível por personagem no HTML fornecido, mas é C0 para a main TL)
                        constellation: str = "C0"  # GenshinLab geralmente foca em C0 para a Tier List principal

                        # Papel/Role: Não está direto no card do personagem.
                        # Podemos inferir pelo contexto ou deixar Unknown.
                        # Para GenshinLab, a role não está clara no snippet.
                        # GenshinLab nao tem a role no card.
                        role: str = "Unknown Role"

                        # Elemento: Também não está no card. Precisaremos enriquecer.
                        element: str = "Unknown"

                        # --- Enriquecer dados com Elemento e Raridade (se não encontrado) do nosso backend ---
                        backend_char_data = all_backend_characters_map.get(
                            character_id_from_site)
                        if backend_char_data:
                            element = backend_char_data.get('element', element)
                            # Usar a raridade do nosso backend se nao pegamos do site ou se for mais confiavel
                            rarity = backend_char_data.get('rarity', rarity)
                            # Se a role nao foi pega, tentar do backend
                            # Se tiver role no seu data_loader
                            role = backend_char_data.get('role', role)

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
                            "role": role,
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

# Nao ha bloco if __name__ == "__main__" aqui. O orquestrador chamará.
