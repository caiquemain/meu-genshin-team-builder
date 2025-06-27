# data_parser.py
import json
import re
import asyncio
from config import SUPPORTED_LANGUAGES
from api_client import APIClient
import aiohttp


class DataParser:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.item_translations_cache = {}

    # --- MÉTODOS AUXILIARES ---
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

    def _clean_html_tags(self, text) -> str:
        if not isinstance(text, str):
            return ""
        return re.sub(re.compile('<.*?>'), '', text).strip()

    def _clean_name_string(self, name_str: str) -> str:
        if not isinstance(name_str, str):
            return name_str
        quotation_chars = "«»\"‘’“”「」『』„“"
        return re.sub(f"[{re.escape(quotation_chars)}]", "", name_str).strip()

    async def get_translated_text(self, text_id: str) -> dict:
        if not text_id or not str(text_id).isdigit():
            return {}
        text_id = str(text_id)
        if text_id in self.item_translations_cache:
            return self.item_translations_cache[text_id]
        translations = await self.api_client.fetch_item_translations(text_id)
        cleaned_translations = {lang: self._clean_name_string(
            name) for lang, name in translations.items()}
        self.item_translations_cache[text_id] = cleaned_translations
        return cleaned_translations

    async def _get_full_character_data(self, character_id: str) -> dict:
        full_data = {}
        async with aiohttp.ClientSession() as session:
            tasks = [self.api_client.fetch_page_data(
                session, character_id, lang) for lang in SUPPORTED_LANGUAGES]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, lang in enumerate(SUPPORTED_LANGUAGES):
                data = results[i]
                if isinstance(data, dict) and data.get('retcode') == 0 and data['data'].get('page'):
                    full_data[lang] = data['data']['page']
        return full_data

    def _find_component_in_modules(self, page_data, component_id):
        for module in page_data.get('modules', []):
            for component in module.get('components', []):
                if component.get('component_id') == component_id:
                    return component
        return None

    # --- FUNÇÕES DE PARSE DEDICADAS ---

    def _parse_name_and_description(self, full_data):
        name, desc = {}, {}
        for lang, page_data in full_data.items():
            name[lang] = self._clean_name_string(page_data.get('name', "N/A"))
            desc[lang] = self._clean_html_tags(page_data.get('desc', "N/A"))
        return name, desc

    def _parse_rarity(self, full_data):
        for page_data in full_data.values():
            rarity_values = page_data.get("filter_values", {}).get(
                "character_rarity", {}).get("values")
            if rarity_values and (rarity_num_match := re.search(r'(\d+)', rarity_values[0])):
                return int(rarity_num_match.group(1))
        return None

    def _parse_vision_and_weapon(self, full_data):
        vision, weapon = {"label": {}, "value": {}}, {"label": {}, "value": {}}
        element_icon = None
        for lang, page_data in full_data.items():
            filter_values = page_data.get('filter_values', {})
            vision_data = filter_values.get('character_vision', {})
            weapon_data = filter_values.get('character_weapon', {})
            vision['value'][lang] = (vision_data.get('values') or ["N/A"])[0]
            vision['label'][lang] = (vision_data.get(
                'key') or {}).get('text', "N/A")
            if not element_icon and vision_data.get('value_types'):
                element_icon = vision_data['value_types'][0].get('icon')
            weapon['value'][lang] = (weapon_data.get('values') or ["N/A"])[0]
            weapon['label'][lang] = (weapon_data.get(
                'key') or {}).get('text', "N/A")
        return vision, weapon, element_icon

    async def _parse_base_info(self, full_data):
        title, affiliation, birthday, constellation_name = {}, {}, {}, {}
        special_dish = {"id": None, "name": {}, "iconUrl": None}
        namecard = {"id": None, "name": {}, "iconUrl": None}

        keywords = {
            "title": ["title", "título", "称号", "稱號", "호칭", "титул", "titel", "titre", "gelar", "julukan", "ฉายา", "danhhiệu"],
            "affiliation": ["affiliation", "afiliación", "afiliação", "所属", "所屬", "소속", "zugehörigkeit", "принадлежность", "группа", "afiliasi", "สังกัด", "thuộc"],
            "birthday": ["birthday", "aniversário", "cumpleaños", "誕生日", "生日", "생일", "деньрождения", "geburtstag", "anniversaire", "ulangtahun", "วันเกิด", "sinhnhật"],
            "constellation_name": ["constellation", "constelación", "constelação", "命ノ星座", "命之座", "운명의 자리", "созвездие", "sternbild", "konstelasi", "กลุ่มดาว", "cung mệnh"],
            "namecard": ["namecard", "cartãodevisita", "名刺", "名片", "명함", "именнаякарта", "namensschild", "thèmenominal", "tarjetadevisita", "kartunama", "นามบัตร", "danhthiếp"],
            "special_dish": ["specialdish", "pratoespecial", "platilloespecial", "特別料理", "특제요리", "особоеблюдо", "spezialgericht", "platspécial", "hidanganspesialisasi", "อาหารจานพิเศษ", "mónănđặcbiệt"]
        }

        found_dish_info, found_namecard_info = None, None
        for lang, page_data in full_data.items():
            component = self._find_component_in_modules(page_data, 'baseInfo')
            if not component:
                continue

            parsed_data = self._parse_json_string(component.get('data', ''))
            if isinstance(parsed_data, dict) and 'list' in parsed_data:
                for item in parsed_data['list']:
                    key_cleaned = re.sub(
                        r'[:\s]', '', item.get('key', '')).lower()
                    val_list = item.get('value')

                    if val_list and val_list[0]:
                        value = self._clean_html_tags(val_list[0])
                        if any(kw in key_cleaned for kw in keywords['title']):
                            title.setdefault(lang, value)
                        if any(kw in key_cleaned for kw in keywords['affiliation']):
                            affiliation.setdefault(lang, value)
                        if any(kw in key_cleaned for kw in keywords['birthday']):
                            birthday.setdefault(lang, value)
                        if any(kw in key_cleaned for kw in keywords['constellation_name']):
                            constellation_name.setdefault(lang, value)

                    if not found_dish_info and any(kw in key_cleaned for kw in keywords['special_dish']):
                        if val_list and val_list[0] and (parsed_dish := self._parse_json_string(val_list[0])):
                            dish_obj = parsed_dish[0] if isinstance(
                                parsed_dish, list) and parsed_dish else parsed_dish
                            if isinstance(dish_obj, dict) and dish_obj.get("ep_id"):
                                found_dish_info = dish_obj

                    if not found_namecard_info and any(kw in key_cleaned for kw in keywords['namecard']):
                        if val_list and val_list[0] and (parsed_card := self._parse_json_string(val_list[0])):
                            card_obj = parsed_card[0] if isinstance(
                                parsed_card, list) and parsed_card else parsed_card
                            if isinstance(card_obj, dict) and card_obj.get("ep_id"):
                                found_namecard_info = card_obj

        for lang in SUPPORTED_LANGUAGES:
            title.setdefault(lang, "N/A")
            affiliation.setdefault(lang, "N/A")
            birthday.setdefault(lang, "N/A")
            constellation_name.setdefault(lang, "N/A")

        if found_dish_info:
            dish_id = str(found_dish_info.get("ep_id"))
            icon_url = found_dish_info.get("icon")
            special_dish["id"] = int(dish_id)
            special_dish["iconUrl"] = icon_url.replace(
                ' ', '%20') if icon_url else None
            special_dish["name"] = await self.get_translated_text(dish_id)

        if found_namecard_info:
            card_id = str(found_namecard_info.get("ep_id"))
            icon_url = found_namecard_info.get("icon")
            namecard["id"] = int(card_id)
            namecard["iconUrl"] = icon_url.replace(
                ' ', '%20') if icon_url else None
            namecard["name"] = await self.get_translated_text(card_id)

        return title, affiliation, birthday, special_dish, constellation_name, namecard

    def _process_ascension_stats(self, stats_by_lang):
        stats_list = []
        base_stats = next(iter(stats_by_lang.values()), [])
        for i, base_stat in enumerate(base_stats):
            if not base_stat.get('key'):
                continue
            labels = {lang: self._clean_html_tags(stats[i].get(
                'key')) for lang, stats in stats_by_lang.items() if i < len(stats)}
            values = base_stat.get('values', [None, None])
            pre_value = values[0] if values and values[0] not in [
                "-", ""] else None
            post_value = values[1] if values and len(
                values) > 1 and values[1] not in ["-", ""] else None
            stats_list.append({"label": labels, "preAscensionValue": self._clean_html_tags(
                pre_value), "postAscensionValue": self._clean_html_tags(post_value)})
        return stats_list

    async def _process_generic_materials(self, materials_raw):
        materials_list = []
        if not materials_raw:
            return materials_list
        material_tasks = []
        material_map = {}
        items_to_process = [self._parse_json_string(
            item) for item in materials_raw]
        flat_items = []
        for item in items_to_process:
            if isinstance(item, list):
                flat_items.extend(item)
            else:
                flat_items.append(item)
        for raw_mat in flat_items:
            if not isinstance(raw_mat, dict):
                continue
            mat_id = str(raw_mat.get('ep_id'))
            if mat_id and mat_id != 'None' and mat_id not in material_map:
                icon_url = raw_mat.get('img') or raw_mat.get('icon')
                material_map[mat_id] = {"id": mat_id, "iconUrl": icon_url.replace(
                    ' ', '%20') if icon_url else None, "amount": raw_mat.get('amount')}
                material_tasks.append(self.get_translated_text(mat_id))

        translated_names_list = await asyncio.gather(*material_tasks, return_exceptions=True)
        for i, mat_id in enumerate(material_map.keys()):
            if not isinstance(translated_names_list[i], Exception):
                material_map[mat_id]["name"] = translated_names_list[i]
                materials_list.append(material_map[mat_id])
        return materials_list

    async def _parse_ascension_data(self, full_character_data_by_lang: dict):
        attributes_list, materials_list = [], []
        aggregated_data = {}

        for lang, page_data in full_character_data_by_lang.items():
            component = self._find_component_in_modules(page_data, 'ascension')
            if not component:
                continue

            parsed_data = self._parse_json_string(component.get('data', ''))
            if isinstance(parsed_data, dict) and (parsed_list := parsed_data.get('list', [])):
                for i, level_data in enumerate(parsed_list):
                    level_key = i
                    if level_key not in aggregated_data:
                        aggregated_data[level_key] = {
                            "level_names": {}, "stats_by_lang": {}, "materials_raw": []}

                    aggregated_data[level_key]['level_names'][lang] = self._clean_html_tags(
                        level_data.get('key'))
                    aggregated_data[level_key]['stats_by_lang'][lang] = level_data.get(
                        'combatList', [])
                    if not aggregated_data[level_key]['materials_raw']:
                        aggregated_data[level_key]['materials_raw'] = level_data.get(
                            'materials', [])

        for data in aggregated_data.values():
            stats = self._process_ascension_stats(data['stats_by_lang'])
            if stats:
                attributes_list.append(
                    {"level": data['level_names'], "stats": stats})

            materials = await self._process_generic_materials(data['materials_raw'])
            if materials:
                materials_list.append(
                    {"level": data['level_names'], "materials": materials})

        return attributes_list, materials_list

    def _process_talent_attributes(self, attributes_by_lang):
        processed_attrs = []
        base_attrs = next(iter(attributes_by_lang.values()), [])
        for i, base_attr in enumerate(base_attrs):
            if not base_attr.get('key'):
                continue
            labels = {lang: self._clean_html_tags(attrs[i].get(
                'key')) for lang, attrs in attributes_by_lang.items() if i < len(attrs)}
            values = base_attr.get('values', [])
            processed_attrs.append({"label": labels, "values": values})
        return processed_attrs

    async def _parse_character_talents(self, full_character_data_by_lang: dict):
        talents, talent_attributes, talent_materials = [], [], []
        aggregated_data = {}
        talent_types = ["normal_attack", "elemental_skill", "elemental_burst"]

        for lang, page_data in full_character_data_by_lang.items():
            component = self._find_component_in_modules(page_data, 'talent')
            if not component:
                continue

            parsed_data = self._parse_json_string(component.get('data', ''))
            if isinstance(parsed_data, dict) and (parsed_list := parsed_data.get('list', [])):
                for i, talent_data in enumerate(parsed_list):
                    talent_key = i
                    if talent_key not in aggregated_data:
                        icon_url = talent_data.get('icon_url')
                        aggregated_data[talent_key] = {
                            "name": {}, "description": {}, "attributes_by_lang": {},
                            "materials_by_level": talent_data.get('materials', []),
                            "iconUrl": icon_url.replace(' ', '%20') if icon_url else None
                        }

                    aggregated_data[talent_key]['name'][lang] = self._clean_html_tags(
                        talent_data.get('title', 'N/A'))
                    aggregated_data[talent_key]['description'][lang] = self._clean_html_tags(
                        talent_data.get('desc', 'N/A'))
                    if attributes := talent_data.get('attributes'):
                        aggregated_data[talent_key]['attributes_by_lang'][lang] = attributes

        for i, data in aggregated_data.items():
            talent_type = talent_types[i] if i < len(
                talent_types) else "passive"
            talents.append(
                {"type": talent_type, "name": data['name'], "description": data['description'], "iconUrl": data['iconUrl']})

            if data['attributes_by_lang']:
                processed_attrs = self._process_talent_attributes(
                    data['attributes_by_lang'])
                if processed_attrs:
                    talent_attributes.append(
                        {"type": talent_type, "talentName": data['name'], "attributes": processed_attrs})

            if data['materials_by_level'] and i < len(talent_types):
                materials_per_level = []
                for level_idx, material_group in enumerate(data['materials_by_level']):
                    if level_idx > 0 and material_group:
                        processed_mats = await self._process_generic_materials(material_group)
                        if processed_mats:
                            materials_per_level.append(
                                {"level": level_idx + 1, "items": processed_mats})
                if materials_per_level:
                    talent_materials.append(
                        {"type": talent_type, "talentName": data['name'], "materials": materials_per_level})

        return talents, talent_attributes, talent_materials

    async def _parse_character_constellations(self, full_character_data_by_lang: dict) -> list:
        aggregated_data = {}
        for lang, page_data in full_character_data_by_lang.items():
            component = self._find_component_in_modules(
                page_data, 'summaryList')
            if not component:
                continue
            parsed_data = self._parse_json_string(component.get('data', ''))
            if isinstance(parsed_data, dict) and (parsed_list := parsed_data.get('list', [])):
                for i, const_data in enumerate(parsed_list):
                    const_num = i + 1
                    if const_num not in aggregated_data:
                        icon_url = const_data.get('icon_url')
                        aggregated_data[const_num] = {"id": const_data.get('id'), "constellationNumber": const_num, "name": {
                        }, "description": {}, "iconUrl": icon_url.replace(' ', '%20') if icon_url else None}
                    aggregated_data[const_num]['name'][lang] = self._clean_name_string(
                        const_data.get('name', 'N/A'))
                    aggregated_data[const_num]['description'][lang] = self._clean_html_tags(
                        const_data.get('desc', 'N/A'))
        return sorted(list(aggregated_data.values()), key=lambda x: x["constellationNumber"])

    # --- FUNÇÃO PRINCIPAL ORQUESTRADORA ---
    async def parse_character_basic_info(self, character_id: str, char_initial_data: dict) -> dict:
        full_character_data_by_lang = await self._get_full_character_data(character_id)
        if not full_character_data_by_lang:
            print(
                f"Não foi possível obter dados para o personagem {char_initial_data.get('name')}. Pulando.")
            return {}

        name, description = self._parse_name_and_description(
            full_character_data_by_lang)
        rarity = self._parse_rarity(full_character_data_by_lang)
        vision, weapon, element_icon_url = self._parse_vision_and_weapon(
            full_character_data_by_lang)
        title, affiliation, birthday, special_dish, constellation_name, namecard = await self._parse_base_info(full_character_data_by_lang)
        constellations = await self._parse_character_constellations(full_character_data_by_lang)
        attributes, ascension_materials = await self._parse_ascension_data(full_character_data_by_lang)
        talents, talent_attributes, talent_materials = await self._parse_character_talents(full_character_data_by_lang)

        # Monta o dicionário final na ordem desejada
        en_name = name.get('en-us', char_initial_data.get("name", "")).lower()
        friendly_id = re.sub(r'[^a-z0-9_]+', '', en_name.replace(' ', '_'))

        character_info = {
            "id": friendly_id,
            "wiki_id": char_initial_data.get("entry_page_id"),
            "name": name,
            "title": title,
            "description": description,
            "rarity": rarity,
            "vision": vision,
            "weapon": weapon,
            "characterIconUrl": next(iter(full_character_data_by_lang.values()), {}).get('icon_url', '').replace(' ', '%20'),
            "elementIconUrl": element_icon_url.replace(' ', '%20') if element_icon_url else None,
            "constellationNameOfficial": constellation_name,
            "specialDish": special_dish,
            "namecard": namecard,
            "constellations": constellations,
            "talents": talents,
            "talentAttributes": talent_attributes,
            "talentMaterials": talent_materials,
            "affiliation": affiliation,
            "birthday": birthday,
            "ascensionMaterials": ascension_materials,
            "attributes": attributes
        }

        return character_info
