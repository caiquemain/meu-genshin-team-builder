# data_parser.py (versão com lógica de exclusão robusta e filtros de segurança)
import json
import re
import asyncio
import html
from config import SUPPORTED_LANGUAGES
from api_client import APIClient
import aiohttp

# DICIONÁRIO DE TRADUÇÕES PARA SUB-STATUS DE ARMAS
SUBSTAT_TRANSLATIONS = {
    "ATK": {"pt-pt": "ATQ%", "en-us": "ATK", "ja-jp": "攻撃力", "zh-cn": "攻击力", "ko-kr": "공격력", "ru-ru": "Сила атаки", "de-de": "ANG", "fr-fr": "ATQ", "es-es": "ATQ", "id-id": "ATK", "th-th": "พลังโจมตี", "vi-vn": "Tấn Công", "zh-tw": "攻擊力"},
    "ATK Percentage": {"pt-pt": "ATQ%", "en-us": "ATK", "ja-jp": "攻撃力", "zh-cn": "攻击力", "ko-kr": "공격력", "ru-ru": "Сила атаки", "de-de": "ANG", "fr-fr": "ATQ", "es-es": "ATQ", "id-id": "ATK", "th-th": "พลังโจมตี", "vi-vn": "Tấn Công", "zh-tw": "攻擊力"},
    "DEF": {"pt-pt": "DEF%", "en-us": "DEF", "ja-jp": "防御力", "zh-cn": "防御力", "ko-kr": "방어력", "ru-ru": "Защита", "de-de": "VTD", "fr-fr": "DÉF", "es-es": "DEF", "id-id": "DEF", "th-th": "พลังป้องกัน", "vi-vn": "Phòng Ngự", "zh-tw": "防禦力"},
    "HP": {"pt-pt": "Vida%", "en-us": "HP", "ja-jp": "HP", "zh-cn": "生命值", "ko-kr": "HP", "ru-ru": "HP", "de-de": "LP", "fr-fr": "PV", "es-es": "Vida", "id-id": "HP", "th-th": "พลังชีวิต", "vi-vn": "HP", "zh-tw": "生命值"},
    "HP Percentage": {"pt-pt": "Vida%", "en-us": "HP", "ja-jp": "HP", "zh-cn": "生命值", "ko-kr": "HP", "ru-ru": "HP", "de-de": "LP", "fr-fr": "PV", "es-es": "Vida", "id-id": "HP", "th-th": "พลังชีวิต", "vi-vn": "HP", "zh-tw": "生命值"},
    "Elemental Mastery": {"pt-pt": "Proficiência Elemental", "en-us": "Elemental Mastery", "ja-jp": "元素熟知", "zh-cn": "元素精通", "ko-kr": "원소 마스터리", "ru-ru": "Мастерство стихий", "de-de": "Elementarkunde", "fr-fr": "Maîtrise élémentaire", "es-es": "Maestría Elemental", "id-id": "Elemental Mastery", "th-th": "ชำนาญธาตุ", "vi-vn": "Tinh Thông Nguyên Tố", "zh-tw": "元素精通"},
    "Energy Recharge": {"pt-pt": "Recarga de Energia%", "en-us": "Energy Recharge", "ja-jp": "元素チャージ効率", "zh-cn": "元素充能效率", "ko-kr": "원소 충전 효율", "ru-ru": "Восст. энергии", "de-de": "Aufladerate", "fr-fr": "Recharge d'énergie", "es-es": "Recarga de Energía", "id-id": "Energy Recharge", "th-th": "การฟื้นฟูพลังงาน", "vi-vn": "Hiệu Quả Nạp Nguyên Tố", "zh-tw": "元素充能效率"},
    "CRIT Rate": {"pt-pt": "Taxa CRIT%", "en-us": "CRIT Rate", "ja-jp": "会心率", "zh-cn": "暴击率", "ko-kr": "치명타 확률", "ru-ru": "Шанс крит. попад.", "de-de": "KT", "fr-fr": "Taux CRIT", "es-es": "Prob. CRIT", "id-id": "CRIT Rate", "th-th": "อัตราคริ", "vi-vn": "Tỷ Lệ Bạo Kích", "zh-tw": "暴擊率"},
    "CRIT DMG": {"pt-pt": "Dano CRIT%", "en-us": "CRIT DMG", "ja-jp": "会心ダメージ", "zh-cn": "暴击伤害", "ko-kr": "치명타 피해", "ru-ru": "Крит. урон", "de-de": "KSCH", "fr-fr": "DGT CRIT", "es-es": "Daño CRIT", "id-id": "CRIT DMG", "th-th": "ความแรงคริ", "vi-vn": "Sát Thương Bạo Kích", "zh-tw": "暴擊傷害"},
    "Physical DMG Bonus": {"pt-pt": "Bônus de Dano Físico%", "en-us": "Physical DMG Bonus", "ja-jp": "物理ダメージ", "zh-cn": "物理伤害加成", "ko-kr": "물리 피해 보너스", "ru-ru": "Бонус физ. урона", "de-de": "Physischer SCH-Bonus", "fr-fr": "Bonus de DGT physiques", "es-es": "Bono de Daño Físico", "id-id": "Physical DMG Bonus", "th-th": "โบนัสความเสียหายกายภาพ", "vi-vn": "Tăng Sát Thương Vật Lý", "zh-tw": "物理傷害加成"}
}

# MAPA DE TRADUÇÕES PARA CHAVES PADRÃO DA SEÇÃO baseInfo
STANDARD_INFO_KEYS = {
    'name': ['name', 'nome', 'Имя:', '和名 / 英名', '名称', '이름', 'Nom', 'Nombre', 'Nama', 'ชื่อ', 'Tên', '名稱'],
    'region': ['region', 'região', 'Регион:', '所属エリア', '地区', '지역', 'Herkunft', 'Région', 'Región', 'พื้นที่', 'Khu Vực', '地區'],
    'source': ['source', 'fonte', 'Где найти:', 'Источник:', '入手方法', '获取途径', '획득 경로', 'Quelle', 'Fuente', 'Sumber', 'ช่องทางได้รับ', 'Nguồn', '獲取途徑', 'Disponibilità', 'หาได้จาก', 'Cómo se consigue', 'Nguồn Gốc', 'Cómo se consigue','Где найти:'],
    'type': ['type', 'tipo', 'Тип:', 'タイプ', '类型', '유형', 'Typ', 'Épée à une main', 'Épée à deux mains', 'Arme d\'hast', 'Arc', 'Catalyseur', 'Tipe', 'ประเภท', 'Loại', '類型'],
    'secondary_attributes': ['secondary attributes', 'atributo secundário', 'atributos secundários', 'Atributo Secundario', 'Дополнительные характеристики:', 'サブステータス', '副属性', '보조 속성', 'Nebenattribute', 'Attributs secondaires', 'Atribut Sekunder', 'ค่าสถานะรอง', 'Thuộc Tính Phụ', '副屬性'],
    'version_released': ['version released', 'disponível na versão', 'versão lançada', 'Версия выхода оружия:', '実装Ver.', '实装版本', '등장 버전', 'Veröffentlichung', 'Ajout à la version', 'Versión de lanzamiento', 'Dirilis pada Versi', 'เวอร์ชันที่ปรากฎ', 'Phiên Bản Ra Mắt', '實裝版本'],
    'refinement_materials': ['Материалы пробуждения:', 'Nguyên Liệu Tinh Luyện']
}
ALL_STANDARD_KEYS_LOWER = {
    val.lower().strip(":") for key_list in STANDARD_INFO_KEYS.values() for val in key_list}


class DataParser:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.item_translations_cache = {}

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
        return html.unescape(re.sub(re.compile('<.*?>'), '', text)).strip()

    def _clean_name_string(self, name_str: str) -> str:
        if not isinstance(name_str, str):
            return name_str
        quotation_chars = "«»\"‘’“”「」『』„“"
        return re.sub(f"[{re.escape(quotation_chars)}]", "", name_str).strip()

    def _normalize_translations(self, trans_dict: dict, use_fallback_value=False) -> dict:
        if not isinstance(trans_dict, dict):
            return {}
        fallback_value = "N/A"
        if use_fallback_value:
            fallback_value = trans_dict.get(
                'en-us') or next(iter(trans_dict.values()), "N/A")
        normalized = {}
        for lang in SUPPORTED_LANGUAGES:
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
        cleaned_translations = {lang: self._clean_name_string(
            name) for lang, name in translations.items()}
        self.item_translations_cache[text_id] = self._normalize_translations(
            cleaned_translations)
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
                session, entry_id, lang) for lang in SUPPORTED_LANGUAGES]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, lang in enumerate(SUPPORTED_LANGUAGES):
                data = results[i]
                if isinstance(data, dict) and data.get('retcode') == 0 and data['data'].get('page'):
                    full_data[lang] = data['data']['page']
        return full_data

    async def _process_generic_materials(self, materials_raw):
        materials_list = []
        if not materials_raw:
            return materials_list
        material_tasks, material_map = [], {}
        items_to_process = [self._parse_json_string(
            item) for item in materials_raw]
        flat_items = [item for sublist in items_to_process for item in (
            sublist if isinstance(sublist, list) else [sublist])]
        for raw_mat in flat_items:
            if not isinstance(raw_mat, dict):
                continue
            mat_id = str(raw_mat.get('ep_id'))
            if mat_id and mat_id != 'None' and mat_id not in material_map:
                icon_url = raw_mat.get('img') or raw_mat.get('icon')
                mat_id_int = int(mat_id) if mat_id.isdigit() else 0
                if not mat_id_int:
                    continue
                material_map[mat_id] = {"id": mat_id_int, "iconUrl": icon_url.replace(
                    ' ', '%20') if icon_url else None, "amount": raw_mat.get('amount')}
                material_tasks.append(self.get_translated_text(mat_id))
        translated_names_list = await asyncio.gather(*material_tasks, return_exceptions=True)
        for i, mat_id in enumerate(list(material_map.keys())):
            if not isinstance(translated_names_list[i], Exception):
                material_map[mat_id]["name"] = translated_names_list[i]
                materials_list.append(material_map[mat_id])
        return materials_list

    # --- PARSER DE ARMAS ---
    def _parse_weapon_rarity_and_type(self, full_data):
        rarity, weapon_type = None, {"value": {}}
        first_page = next(iter(full_data.values()), {})
        if not first_page:
            return None, {}
        filter_values = first_page.get("filter_values", {})
        if rarity_data := filter_values.get("weapon_rarity"):
            if values := rarity_data.get("value_types"):
                if enum_str := values[0].get("enum_string"):
                    if enum_str.isdigit():
                        rarity = int(enum_str)
        for lang, page_data in full_data.items():
            lang_filters = page_data.get('filter_values', {})
            if type_data := lang_filters.get('weapon_type'):
                weapon_type['value'][lang] = (
                    type_data.get('values') or ["N/A"])[0]
        return rarity, self._normalize_translations(weapon_type['value'])

    def _parse_weapon_base_info_and_passive(self, full_data):
        sub_stat_key, passive_name, passive_desc = "", {}, {}

        en_us_page_data = full_data.get('en-us', {})
        if en_us_page_data and (component := self._find_component_in_modules(en_us_page_data, 'baseInfo')):
            parsed_data = self._parse_json_string(component.get('data', ''))
            data_list = parsed_data.get('list', []) if isinstance(
                parsed_data, dict) else []
            for item in data_list:
                key_lower = self._clean_html_tags(item.get('key', '')).lower()
                if any(s in key_lower for s in STANDARD_INFO_KEYS['secondary_attributes']):
                    value_list = item.get('value')
                    if value_list and value_list[0]:
                        sub_stat_key = self._clean_html_tags(value_list[0])
                    break

        for lang, page_data in full_data.items():
            if component := self._find_component_in_modules(page_data, 'baseInfo'):
                parsed_data = self._parse_json_string(
                    component.get('data', ''))
                data_list = parsed_data.get('list', []) if isinstance(
                    parsed_data, dict) else []
                for item in data_list:
                    key_clean = self._clean_html_tags(item.get('key', ''))
                    if key_clean.lower().strip(":") not in ALL_STANDARD_KEYS_LOWER:
                        value_list = item.get('value')
                        desc_text = self._clean_html_tags(
                            value_list[0]) if value_list and value_list[0] else ""
                        if len(desc_text) > 20:
                            passive_name[lang] = key_clean
                            passive_desc[lang] = desc_text
                            break

        return sub_stat_key, passive_name, passive_desc

    async def _parse_weapon_ascension(self, full_data):
        attributes, materials = [], []
        ascension_data = {}
        for lang, page_data in full_data.items():
            component = self._find_component_in_modules(page_data, 'ascension')
            if not component:
                continue
            parsed_component_data = self._parse_json_string(
                component.get('data', ''))
            parsed_list = parsed_component_data.get(
                'list', []) if isinstance(parsed_component_data, dict) else []
            for i, level_info in enumerate(parsed_list):
                level_key = i
                if level_key not in ascension_data:
                    ascension_data[level_key] = {'level_name': {}, 'stats': {
                    }, 'materials_raw': level_info.get('materials', [])}
                ascension_data[level_key]['level_name'][lang] = self._clean_html_tags(
                    level_info.get('key'))
                combat_list = level_info.get('combatList')
                if combat_list and len(combat_list) > 1:
                    ascension_data[level_key]['stats'][lang] = {
                        'headers': [self._clean_html_tags(h) for h in combat_list[0].get('values', [])],
                        'values': [self._clean_html_tags(v) for v in combat_list[1].get('values', [])]
                    }

        for level_key, data in ascension_data.items():
            level_name = self._normalize_translations(
                data['level_name'], use_fallback_value=True)
            mats = await self._process_generic_materials(data['materials_raw'])
            if mats:
                materials.append({'level': level_name, 'materials': mats})
            if stats_by_lang := data.get('stats', {}):
                stat_list = []
                ref_lang_data = stats_by_lang.get(
                    'en-us') or next(iter(stats_by_lang.values()), None)
                if not ref_lang_data:
                    continue
                ref_headers, ref_values = ref_lang_data.get(
                    'headers', []), ref_lang_data.get('values', [])
                if len(ref_headers) >= 2:
                    base_atk_label_translations = {lang: stats['headers'][0] for lang, stats in stats_by_lang.items(
                    ) if len(stats.get('headers', [])) > 0}
                    stat_list.append({'label': self._normalize_translations(base_atk_label_translations, use_fallback_value=True),
                                     'preAscensionValue': ref_values[0] if ref_values[0] != '-' else None, 'postAscensionValue': ref_values[1] if ref_values[1] != '-' else None})
                if len(ref_headers) >= 3:
                    sub_stat_label_translations = {lang: stats['headers'][2] for lang, stats in stats_by_lang.items(
                    ) if len(stats.get('headers', [])) > 2}
                    stat_list.append({'label': self._normalize_translations(
                        sub_stat_label_translations, use_fallback_value=True), 'value': ref_values[2] if ref_values[2] != '-' else None})
                if stat_list:
                    attributes.append(
                        {'level': level_name, 'stats': stat_list})
        return attributes, materials

    async def parse_weapon_info(self, weapon_id: str, weapon_initial_data: dict) -> dict:
        full_weapon_data = await self._get_full_data_for_entry(weapon_id)
        if not full_weapon_data:
            print(
                f"Não foi possível obter dados para a arma {weapon_initial_data.get('name')}. Pulando.")
            return {}
        name, description = {}, {}
        for lang, page_data in full_weapon_data.items():
            name[lang] = self._clean_name_string(page_data.get('name', "N/A"))
            description[lang] = self._clean_html_tags(
                page_data.get('desc', "N/A"))
        rarity, weapon_type_values = self._parse_weapon_rarity_and_type(
            full_weapon_data)
        sub_stat_key, passive_name, passive_desc = self._parse_weapon_base_info_and_passive(
            full_weapon_data)
        attributes, ascension_materials = await self._parse_weapon_ascension(full_weapon_data)
        weapon_icon = ""
        for page_data in full_weapon_data.values():
            if page_data.get("icon_url"):
                weapon_icon = page_data.get("icon_url").replace(' ', '%20')
                break
        en_name = name.get(
            'en-us', weapon_initial_data.get("name", "")).lower()
        friendly_id = re.sub(r'[^a-z0-9_]+', '', en_name.replace(' ', '_'))
        wiki_id_raw = weapon_initial_data.get("entry_page_id")
        wiki_id = int(wiki_id_raw) if wiki_id_raw and str(
            wiki_id_raw).isdigit() else None
        sub_stat_translations = SUBSTAT_TRANSLATIONS.get(
            sub_stat_key.strip(), {})
        weapon_info = {
            "id": friendly_id, "wiki_id": wiki_id,
            "name": self._normalize_translations(name),
            "description": self._normalize_translations(description),
            "rarity": rarity, "type": weapon_type_values,
            "subStat": self._normalize_translations(sub_stat_translations),
            "passiveName": self._normalize_translations(passive_name),
            "passiveDescription": self._normalize_translations(passive_desc),
            "weaponIconUrl": weapon_icon,
            "ascensionMaterials": ascension_materials, "attributes": attributes
        }
        return weapon_info

    # --- PARSER DE PERSONAGENS ---
    async def parse_character_basic_info(self, character_id: str, char_initial_data: dict) -> dict:
        full_character_data_by_lang = await self._get_full_data_for_entry(character_id)
        if not full_character_data_by_lang:
            print(
                f"Não foi possível obter dados para o personagem {char_initial_data.get('name')}. Pulando.")
            return {}
        name, description = self._parse_char_name_and_description(
            full_character_data_by_lang)
        rarity = self._parse_char_rarity(full_character_data_by_lang)
        vision, weapon, element_icon_url = self._parse_char_vision_and_weapon(
            full_character_data_by_lang)
        title, affiliation, birthday, special_dish, constellation_name, namecard = await self._parse_char_base_info(full_character_data_by_lang)
        constellations = await self._parse_character_constellations(full_character_data_by_lang)
        attributes, ascension_materials = await self._parse_char_ascension_data(full_character_data_by_lang)
        talents, talent_attributes, talent_materials = await self._parse_character_talents(full_character_data_by_lang)
        en_name = name.get('en-us', char_initial_data.get("name", "")).lower()
        friendly_id = re.sub(r'[^a-z0-9_]+', '', en_name.replace(' ', '_'))
        character_info = {
            "id": friendly_id, "wiki_id": char_initial_data.get("entry_page_id"),
            "name": self._normalize_translations(name),
            "title": self._normalize_translations(title),
            "description": self._normalize_translations(description),
            "rarity": rarity,
            "vision": self._normalize_translations(vision['value'], True),
            "weapon": self._normalize_translations(weapon['value'], True),
            "characterIconUrl": next(iter(full_character_data_by_lang.values()), {}).get('icon_url', '').replace(' ', '%20'),
            "elementIconUrl": element_icon_url.replace(' ', '%20') if element_icon_url else None,
            "constellationNameOfficial": self._normalize_translations(constellation_name),
            "specialDish": special_dish, "namecard": namecard, "constellations": constellations, "talents": talents,
            "talentAttributes": talent_attributes, "talentMaterials": talent_materials,
            "affiliation": self._normalize_translations(affiliation),
            "birthday": self._normalize_translations(birthday, True),
            "ascensionMaterials": ascension_materials,
            "attributes": attributes
        }
        return character_info

    def _parse_char_name_and_description(self, full_data):
        name, desc = {}, {}
        for lang, page_data in full_data.items():
            name[lang] = self._clean_name_string(page_data.get('name', "N/A"))
            desc[lang] = self._clean_html_tags(page_data.get('desc', "N/A"))
        return name, desc

    def _parse_char_rarity(self, full_data):
        for page_data in full_data.values():
            rarity_values = page_data.get("filter_values", {}).get(
                "character_rarity", {}).get("values")
            if rarity_values and (rarity_num_match := re.search(r'(\d+)', rarity_values[0])):
                return int(rarity_num_match.group(1))
        return None

    def _parse_char_vision_and_weapon(self, full_data):
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

    async def _parse_char_base_info(self, full_data):
        title, affiliation, birthday, constellation_name = {}, {}, {}, {}
        special_dish, namecard = {"id": None, "name": {}, "iconUrl": None}, {
            "id": None, "name": {}, "iconUrl": None}
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
            dish_id, icon_url = str(found_dish_info.get(
                "ep_id")), found_dish_info.get("icon")
            special_dish.update({"id": int(dish_id) if dish_id.isdigit() else None, "iconUrl": icon_url.replace(' ', '%20') if icon_url else None, "name": await self.get_translated_text(dish_id)})
        if found_namecard_info:
            card_id, icon_url = str(found_namecard_info.get(
                "ep_id")), found_namecard_info.get("icon")
            namecard.update({"id": int(card_id) if card_id.isdigit() else None, "iconUrl": icon_url.replace(' ', '%20') if icon_url else None, "name": await self.get_translated_text(card_id)})
        return title, affiliation, birthday, special_dish, constellation_name, namecard

    async def _parse_char_ascension_data(self, full_character_data_by_lang: dict):
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
            if stats := self._process_char_ascension_stats(data['stats_by_lang']):
                attributes_list.append({"level": self._normalize_translations(
                    data['level_names'], True), "stats": stats})
            if materials := await self._process_generic_materials(data['materials_raw']):
                materials_list.append({"level": self._normalize_translations(
                    data['level_names'], True), "materials": materials})
        return attributes_list, materials_list

    def _process_char_ascension_stats(self, stats_by_lang):
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
            post_value = values[1] if len(values) > 1 and values[1] not in [
                "-", ""] else None
            stats_list.append({"label": self._normalize_translations(labels, True), "preAscensionValue": self._clean_html_tags(
                pre_value), "postAscensionValue": self._clean_html_tags(post_value)})
        return stats_list

    def _process_talent_attributes(self, attributes_by_lang):
        processed_attrs, base_attrs = [], next(
            iter(attributes_by_lang.values()), [])
        for i, base_attr in enumerate(base_attrs):
            if not base_attr.get('key'):
                continue
            labels = {lang: self._clean_html_tags(attrs[i].get(
                'key')) for lang, attrs in attributes_by_lang.items() if i < len(attrs)}
            processed_attrs.append({"label": self._normalize_translations(
                labels, True), "values": base_attr.get('values', [])})
        return processed_attrs

    async def _parse_character_talents(self, full_character_data_by_lang: dict):
        talents, talent_attributes, talent_materials = [], [], []
        aggregated_data, talent_types = {}, [
            "normal_attack", "elemental_skill", "elemental_burst"]
        for lang, page_data in full_character_data_by_lang.items():
            component = self._find_component_in_modules(page_data, 'talent')
            if not component:
                continue
            parsed_data = self._parse_json_string(component.get('data', ''))
            if isinstance(parsed_data, dict) and (parsed_list := parsed_data.get('list', [])):
                for i, talent_data in enumerate(parsed_list):
                    if i not in aggregated_data:
                        icon_url = talent_data.get('icon_url')
                        aggregated_data[i] = {"name": {}, "description": {}, "attributes_by_lang": {}, "materials_by_level": talent_data.get(
                            'materials', []), "iconUrl": icon_url.replace(' ', '%20') if icon_url else None}
                    aggregated_data[i]['name'][lang] = self._clean_html_tags(
                        talent_data.get('title', 'N/A'))
                    aggregated_data[i]['description'][lang] = self._clean_html_tags(
                        talent_data.get('desc', 'N/A'))
                    if attributes := talent_data.get('attributes'):
                        aggregated_data[i]['attributes_by_lang'][lang] = attributes
        for i, data in aggregated_data.items():
            talent_type = talent_types[i] if i < len(
                talent_types) else "passive"
            talents.append({"type": talent_type, "name": self._normalize_translations(
                data['name']), "description": self._normalize_translations(data['description']), "iconUrl": data['iconUrl']})
            if data['attributes_by_lang'] and (processed_attrs := self._process_talent_attributes(data['attributes_by_lang'])):
                talent_attributes.append({"type": talent_type, "talentName": self._normalize_translations(
                    data['name']), "attributes": processed_attrs})
            if data['materials_by_level'] and i < len(talent_types):
                materials_per_level = []
                for level_idx, material_group in enumerate(data['materials_by_level']):
                    if level_idx > 0 and material_group and (processed_mats := await self._process_generic_materials(material_group)):
                        materials_per_level.append(
                            {"level": level_idx + 1, "items": processed_mats})
                if materials_per_level:
                    talent_materials.append({"type": talent_type, "talentName": self._normalize_translations(
                        data['name']), "materials": materials_per_level})
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
        final_list = []
        for const_data in sorted(list(aggregated_data.values()), key=lambda x: x["constellationNumber"]):
            const_data["name"] = self._normalize_translations(
                const_data["name"])
            const_data["description"] = self._normalize_translations(
                const_data["description"])
            final_list.append(const_data)
        return final_list
