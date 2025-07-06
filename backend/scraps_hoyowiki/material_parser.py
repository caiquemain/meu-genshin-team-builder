import re
import json
from base_parser import BaseParser
import config


class MaterialParser(BaseParser):
    """
    Parser especializado para extrair e processar dados detalhados de materiais.
    """

    async def parse_material_info(self, material_id: str, material_initial_data: dict) -> dict:
        full_material_data = await self._get_full_data_for_entry(material_id)
        if not full_material_data:
            print(
                f"Não foi possível obter dados para o material ID {material_id}. Pulando.")
            return {}

        name, description, raw_material_type, raw_sources = {}, {}, {}, {}
        icon_url = ""

        first_page = next(iter(full_material_data.values()), {})
        icon_url_raw = first_page.get("icon_url")
        if icon_url_raw:
            icon_url = icon_url_raw.replace(' ', '%20')

        for lang, page_data in full_material_data.items():
            name[lang] = self._clean_name_string(page_data.get('name', ""))
            description[lang] = self._clean_html_tags(
                page_data.get('desc', ""))

            if component := self._find_component_in_modules(page_data, 'baseInfo'):
                parsed_data = self._parse_json_string(
                    component.get('data', ''))
                data_list = parsed_data.get('list', []) if isinstance(
                    parsed_data, dict) else []

                for item in data_list:
                    key_clean = self._clean_html_tags(item.get('key', ''))
                    key_lower = re.sub(
                        r'\s+', ' ', key_clean).lower().strip(":")
                    value_list = item.get('value', [])
                    if not value_list:
                        continue

                    if any(kw in key_lower for kw in config.MATERIAL_INFO_KEYS['type']):
                        raw_material_type[lang] = value_list[0]
                    elif any(kw in key_lower for kw in config.MATERIAL_INFO_KEYS['source']):
                        if lang not in raw_sources:
                            raw_sources[lang] = []
                        raw_sources[lang].extend(value_list)

        cleaned_material_type = {lang: self._clean_html_tags(
            val) for lang, val in raw_material_type.items()}

        cleaned_sources = {}
        for lang, source_html_list in raw_sources.items():
            lang_sources = []
            for source_html in source_html_list:
                if source_html.startswith('$[{'):
                    parsed_item = self._parse_json_string(source_html)
                    item_name = (parsed_item[0] if isinstance(
                        parsed_item, list) else parsed_item).get('name')
                    if item_name:
                        # --- AQUI ESTÁ A CORREÇÃO ---
                        # Pega o prefixo traduzido do nosso novo dicionário de config
                        synthesis_prefix = config.SYNTHESIS_KEYWORDS.get(
                            lang, "Synthesis")
                        lang_sources.append(f"{synthesis_prefix}: {item_name}")
                else:
                    lang_sources.extend(
                        self._parse_html_list_string(source_html))

            if lang_sources:
                cleaned_sources[lang] = lang_sources

        wiki_id = int(material_id) if material_id.isdigit() else None
        en_name = name.get(
            'en-us', material_initial_data.get("name", "")).lower()
        friendly_id = re.sub(r'[^a-z0-9_]+', '', en_name.replace(' ', '_'))

        material_info = {
            "id": friendly_id,
            "wiki_id": wiki_id,
            "name": self._normalize_translations(name, use_fallback_value=True),
            "description": self._normalize_translations(description),
            "type": self._normalize_translations(cleaned_material_type, use_fallback_value=True),
            "sources": self._normalize_translations(cleaned_sources, fallback_default=["N/A"]),
            "iconUrl": icon_url,
        }
        return material_info
