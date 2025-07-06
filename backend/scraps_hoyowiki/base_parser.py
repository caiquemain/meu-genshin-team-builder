import json
import re
import asyncio
import html
import os
import aiohttp
from api_client import APIClient
import config


class BaseParser:
    """Classe base que contém a lógica compartilhada por todos os parsers."""

    def __init__(self, api_client: 'APIClient'):
        self.api_client = api_client
        self.item_translations_cache = {}
        self.materials_db = {}

    def load_materials_from_disk(self, materials_dir: str):
        if not os.path.isdir(materials_dir):
            return
        print(
            f"\nCarregando banco de dados de materiais de '{materials_dir}'...")
        count = 0
        for filename in os.listdir(materials_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(materials_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        material_data = json.load(f)
                        if 'wiki_id' in material_data and material_data['wiki_id']:
                            self.materials_db[str(
                                material_data['wiki_id'])] = material_data
                            count += 1
                except Exception as e:
                    print(
                        f"  Aviso: Falha ao carregar o material {filename}. Erro: {e}")
        print(f"Carregados {count} materiais no cache do parser.")

    def _parse_json_string(self, json_string: str):
        if not isinstance(json_string, str):
            return json_string
        cleaned_string = json_string.strip()
        if cleaned_string.startswith('$[{') and cleaned_string.endswith('}]$'):
            cleaned_string = cleaned_string[2:-2].replace('\\"', '"')
        try:
            return json.loads(cleaned_string)
        except (json.JSONDecodeError, TypeError):
            return cleaned_string

    def _clean_html_tags(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        return html.unescape(re.sub(re.compile('<.*?>'), '', text)).strip()

    def _parse_html_list_string(self, html_string: str) -> list[str]:
        if not html_string or not isinstance(html_string, str):
            return []
        text_with_delimiters = re.sub(r'</p>|<p>|<br\s*/?>', '|', html_string)
        cleaned_text = self._clean_html_tags(text_with_delimiters)
        return [item.strip() for item in cleaned_text.split('|') if item.strip()]

    def _clean_name_string(self, name_str: str) -> str:
        if not isinstance(name_str, str):
            return name_str
        quotation_chars = "«»\"‘’“”「」『』„“"
        return re.sub(f"[{re.escape(quotation_chars)}]", "", name_str).strip()

    def _normalize_translations(self, trans_dict: dict, use_fallback_value=False, fallback_default=None) -> dict:
        if not isinstance(trans_dict, dict):
            return {}
        fallback_value = fallback_default if fallback_default is not None else "N/A"
        if use_fallback_value:
            fallback_value = trans_dict.get(
                'en-us') or next(iter(trans_dict.values()), fallback_value)
        normalized = {}
        for lang in config.SUPPORTED_LANGUAGES:
            value = trans_dict.get(lang)
            normalized[lang] = value if value else fallback_value
        return normalized

    async def get_translated_text(self, text_id: str) -> dict:
        if not text_id or not str(text_id).isdigit():
            return {}
        text_id = str(text_id)
        if text_id in self.item_translations_cache:
            return self.item_translations_cache[text_id]
        translations = await self.api_client.fetch_item_translations(text_id)
        cleaned = {lang: self._clean_name_string(
            name) for lang, name in translations.items()}
        self.item_translations_cache[text_id] = self._normalize_translations(
            cleaned)
        return self.item_translations_cache[text_id]

    def _find_component_in_modules(self, page_data, component_id):
        for module in page_data.get('modules', []):
            for component in module.get('components', []):
                if component.get('component_id') == component_id:
                    return component
        return None

    async def _get_full_data_for_entry(self, entry_id: str) -> dict:
        full_data = {}
        async with aiohttp.ClientSession() as session:
            tasks = [self.api_client.fetch_page_data(
                session, entry_id, lang) for lang in config.SUPPORTED_LANGUAGES]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, lang in enumerate(config.SUPPORTED_LANGUAGES):
                data = results[i]
                if isinstance(data, dict) and data.get('retcode') == 0 and data['data'].get('page'):
                    full_data[lang] = data['data']['page']
        return full_data

    async def _process_generic_materials(self, materials_raw):
        if not materials_raw:
            return []

        materials_list = []

        new_ids_to_fetch_names = {}
        material_objects_to_fill = {}

        for material_string_blob in materials_raw:
            parsed_mat = self._parse_json_string(material_string_blob)

            raw_mat = None
            if isinstance(parsed_mat, list) and parsed_mat:
                raw_mat = parsed_mat[0]
            elif isinstance(parsed_mat, dict):
                raw_mat = parsed_mat
            else:
                continue

            mat_id = str(raw_mat.get('ep_id'))
            if not (mat_id and mat_id.isdigit()):
                continue

            amount = raw_mat.get('amount')

            if mat_id in self.materials_db:
                cached_material = self.materials_db[mat_id]
                material_obj = {
                    "id": cached_material.get('id'),
                    # <-- ADICIONADO AQUI
                    "wiki_id": cached_material.get('wiki_id'),
                    "amount": amount,
                    "iconUrl": cached_material.get('iconUrl'),
                    "name": cached_material.get('name', {})
                }
                materials_list.append(material_obj)
            else:
                icon_url_raw = raw_mat.get('img') or raw_mat.get('icon')
                new_material = {
                    "id": None,
                    "wiki_id": int(mat_id),  # <-- ADICIONADO AQUI
                    "amount": amount,
                    "iconUrl": icon_url_raw.replace(' ', '%20') if icon_url_raw else None,
                    "name": {}
                }
                materials_list.append(new_material)

                if mat_id not in new_ids_to_fetch_names:
                    new_ids_to_fetch_names[mat_id] = self.get_translated_text(
                        mat_id)

                if mat_id not in material_objects_to_fill:
                    material_objects_to_fill[mat_id] = []
                material_objects_to_fill[mat_id].append(new_material)

        if not new_ids_to_fetch_names:
            return materials_list

        task_ids = list(new_ids_to_fetch_names.keys())
        results = await asyncio.gather(*new_ids_to_fetch_names.values(), return_exceptions=True)

        translated_names_map = {task_ids[i]: result for i, result in enumerate(
            results) if not isinstance(result, Exception)}

        for mat_id, translated_name in translated_names_map.items():
            if mat_id in material_objects_to_fill:
                for material_obj in material_objects_to_fill[mat_id]:
                    material_obj['name'] = translated_name
                    en_name = translated_name.get('en-us', '').lower()
                    material_obj['id'] = re.sub(
                        r'[^a-z0-9_]+', '', en_name.replace(' ', '_'))

        # Remove qualquer objeto que não pôde ser finalizado corretamente
        materials_list = [mat for mat in materials_list if mat.get('id')]

        return materials_list

        # ETAPA 2: Buscar os nomes de todos os materiais novos de uma só vez
        print(
            f"Buscando nomes para {len(new_ids_to_fetch_names)} novos materiais encontrados...")
        task_ids = list(new_ids_to_fetch_names.keys())
        results = await asyncio.gather(*new_ids_to_fetch_names.values(), return_exceptions=True)

        # Mapeia os resultados de volta para os IDs
        translated_names_map = {task_ids[i]: result for i, result in enumerate(
            results) if not isinstance(result, Exception)}

        # ETAPA 3: Finalizar os objetos dos materiais novos com os nomes e IDs corretos
        for material in materials_list:
            # Se o material não tem um 'id' amigável, significa que ele é novo
            if material.get('id') is None:
                # Remove o ID numérico temporário
                numeric_id = material.pop('numeric_id')
                if numeric_id in translated_names_map:
                    translated_name = translated_names_map[numeric_id]
                    material['name'] = translated_name

                    # Gera o ID amigável (slug) a partir do nome em inglês
                    en_name = translated_name.get('en-us', '').lower()
                    material['id'] = re.sub(
                        r'[^a-z0-9_]+', '', en_name.replace(' ', '_'))
                else:
                    # Fallback caso a busca do nome falhe
                    material['id'] = f"unknown_id_{numeric_id}"

        return materials_list
