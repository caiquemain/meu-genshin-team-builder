# backend/app/scrapers/game8_scraper.py
import requests
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any, Optional, Union, cast  # Importe cast

# Importar o mapa de personagens para enriquecer dados
from app.data_loader import get_all_characters_map

GAME8_URL = "https://game8.co/games/Genshin-Impact/archives/297465"


def scrape_game8_co(all_backend_characters_map: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """
    Raspa os dados da Tier List do Game8.co.
    Não usa Selenium. Retorna uma lista de dicionários com os dados padronizados.
    Recebe all_backend_characters_map para enriquecer dados.
    """
    try:
        print(f"Scraping {GAME8_URL} (Site: game8_co)...")
        response = requests.get(GAME8_URL)
        response.raise_for_status()  # Lança uma exceção para erros HTTP (4xx ou 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
        print("Página carregada, extraindo HTML...")

        tier_list_data: List[Dict[str, Any]] = []

        active_tab_panel_raw: Optional[Union[Tag, NavigableString]] = soup.find(
            'div', class_='a-tabPanel is-active')
        active_tab_panel: Optional[Tag] = cast(
            Tag, active_tab_panel_raw) if isinstance(active_tab_panel_raw, Tag) else None

        if not active_tab_panel:
            print(
                "Erro: Não foi possível encontrar o painel da aba ativa (tier list principal) no Game8.co.")
            return None

        tier_table_raw: Optional[Union[Tag, NavigableString]
                                 ] = active_tab_panel.find('table', class_='a-table')
        tier_table: Optional[Tag] = cast(Tag, tier_table_raw) if isinstance(
            tier_table_raw, Tag) else None

        if not tier_table:
            print("Erro: Não foi possível encontrar a tabela da tier list no Game8.co.")
            return None

        role_headers: List[str] = []
        header_row_raw: Optional[Union[Tag,
                                       NavigableString]] = tier_table.find('tr')
        header_row: Optional[Tag] = cast(Tag, header_row_raw) if isinstance(
            header_row_raw, Tag) else None

        if header_row:
            for th in cast(List[Tag], header_row.find_all('th'))[1:]:
                role_headers.append(th.get_text(strip=True))
        else:
            print("Aviso: Não foi possível encontrar a linha de cabeçalho da tabela de papéis no Game8.co. Usando papéis padrão.")
            role_headers = ["Main DPS", "Sub-DPS", "Support"]  # Fallback

        tier_rows_data: List[Tag] = cast(
            List[Tag], tier_table.find_all('tr')[1:])

        for row_tag in tier_rows_data:
            tier_title_element_raw: Optional[Union[Tag, NavigableString]] = row_tag.find(
                'th')
            tier_title_element: Optional[Tag] = cast(
                Tag, tier_title_element_raw) if isinstance(tier_title_element_raw, Tag) else None

            tier_level_img_raw: Optional[Union[Tag, NavigableString]] = tier_title_element.find(
                'img') if tier_title_element else None
            tier_level_img: Optional[Tag] = cast(Tag, tier_level_img_raw) if isinstance(
                tier_level_img_raw, Tag) else None

            tier_level: str = tier_level_img.get('alt', 'Unknown Tier').replace(
                ' Tier', '') if tier_level_img else "Unknown Tier"

            role_cells: List[Tag] = cast(List[Tag], row_tag.find_all('td'))

            for i, role_cell_tag in enumerate(role_cells):
                role_name = role_headers[i] if i < len(
                    role_headers) else "Unknown Role"

                characters_in_cell: List[Tag] = cast(
                    List[Tag], role_cell_tag.find_all('a', class_='a-link'))

                for char_link_tag in characters_in_cell:
                    char_img_raw: Optional[Union[Tag, NavigableString]] = char_link_tag.find(
                        'img')
                    char_img: Optional[Tag] = cast(Tag, char_img_raw) if isinstance(
                        char_img_raw, Tag) else None

                    alt_text: str = char_img.get(
                        'alt', 'Genshin - Unknown Character') if char_img else 'Genshin - Unknown Character'

                    char_name: str = "Unknown"
                    if "Genshin - " in alt_text:
                        # CORREÇÃO AQUI: Limpar " Rank", " DPS Rank", " Support Rank" etc. do nome
                        char_name_part = alt_text.replace(
                            'Genshin - ', '').strip()
                        if ' Rank' in char_name_part:
                            # Remove " Rank", " DPS Rank", " Support Rank", etc.
                            char_name = char_name_part.split(' Rank')[
                                0].strip()
                        # Para pegar só o nome antes de " Rank"
                        elif ' Rank' not in alt_text and ' Genshin - ' in alt_text and char_name_part.endswith(" Rank"):
                            char_name = " ".join(char_name_part.split(" ")[
                                                 :-2]) if len(char_name_part.split(" ")) > 2 else char_name_part.split(" ")[0]
                        else:
                            char_name = char_name_part  # Fallback se nao tiver "Rank"
                    elif alt_text != "Unknown Character":
                        char_name = alt_text

                    # Refinamento para garantir o nome puro
                    # Remova qualquer papel que possa ter ficado (Sub-DPS, Main DPS, Support)
                    char_name = char_name.replace('Main DPS', '').replace(
                        'Sub-DPS', '').replace('Support', '').strip()

                    href_val: Optional[str] = char_link_tag.get('href')
                    character_id_from_site: Optional[str] = None
                    if href_val:
                        segments = [s for s in href_val.strip(
                            '/').split('/') if s]
                        if segments:
                            last_segment = segments[-1]
                            # Usar .lower() e ajustar para "best-builds"
                            character_id_from_site = last_segment.replace(
                                '-best-builds', '').lower()

                    if not character_id_from_site:
                        character_id_from_site = char_name.lower().replace(' ', '_').replace('.', '')

                    # --- Enriquecer dados com Elemento e Raridade do nosso backend ---
                    element: str = "Unknown"
                    rarity: Optional[int] = None
                    constellation: str = "C0"  # Game8 foca em C0 para a Main Tier List

                    backend_char_data = all_backend_characters_map.get(
                        character_id_from_site)
                    if backend_char_data:
                        element = backend_char_data.get('element', element)
                        rarity = backend_char_data.get('rarity', rarity)

                    tier_list_data.append({
                        "character_id": character_id_from_site,
                        "character_name": char_name,  # Agora deve vir limpo
                        "tier_level": tier_level,
                        "role": role_name,
                        "constellation": constellation,
                        "rarity": rarity,
                        "element": element,
                        "source_site": "game8_co"  # Define a fonte do site
                    })

        print(f"Extraídos {len(tier_list_data)} personagens do Game8.co.")
        return tier_list_data

    except requests.exceptions.RequestException as e:
        print(f"Erro de Requisição HTTP para Game8.co: {e}")
        return None
    except Exception as e:
        print(f"Erro ao raspar Game8.co: {e}")
        return None

# Nao ha bloco if __name__ == "__main__" aqui. O orquestrador chamará.
