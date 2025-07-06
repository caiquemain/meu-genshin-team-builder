import re

import json
from base_parser import BaseParser
import config

# --- CONSTANTES ESPECÍFICAS DE PARSING ---

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
    'source': ['source', 'fonte', 'Где найти:', 'Источник:', '入手方法', '获取途径', '획득 경로', 'Quelle', 'Fuente', 'Sumber', 'ช่องทางได้รับ', 'Nguồn', '獲取途徑', 'Disponibilità', 'หาได้จาก', 'Cómo se consigue', 'Nguồn Gốc', 'Cómo se consigue', 'Где найти:'],
    'type': ['type', 'tipo', 'Тип:', 'タイプ', '类型', '유형', 'Typ', 'Épée à une main', 'Épée à deux mains', 'Arme d\'hast', 'Arc', 'Catalyseur', 'Tipe', 'ประเภท', 'Loại', '類型'],
    'secondary_attributes': ['secondary attributes', 'atributo secundário', 'atributos secundários', 'Atributo Secundario', 'Дополнительные характеристики:', 'サブステータス', '副属性', '보조 속성', 'Nebenattribute', 'Attributs secondaires', 'Atribut Sekunder', 'ค่าสถานะรอง', 'Thuộc Tính Phụ', '副屬性'],
    'version_released': ['version released', 'disponível na versão', 'versão lançada', 'Версия выхода оружия:', '実装Ver.', '实装版本', '등장 버전', 'Veröffentlichung', 'Ajout à la version', 'Versión de lanzamiento', 'Dirilis pada Versi', 'เวอร์ชันที่ปรากฎ', 'Phiên Bản Ra Mắt', '實裝版本'],
    'refinement_materials': ['Материалы пробуждения:', 'Nguyên Liệu Tinh Luyện']
}
ALL_STANDARD_KEYS_LOWER = {
    val.lower().strip(":") for key_list in STANDARD_INFO_KEYS.values() for val in key_list}


class WeaponParser(BaseParser):
    """
    Parser especializado para extrair e processar dados detalhados de armas.
    """

    # --- FUNÇÕES AUXILIARES DE PARSING DE ARMAS ---

    def _parse_weapon_rarity_and_type(self, full_data):
        rarity, weapon_type = None, {"value": {}}
        first_page = next(iter(full_data.values()), None)
        if not first_page:
            return None, {}

        filter_values = first_page.get("filter_values")
        if filter_values and isinstance(filter_values, dict):
            rarity_data = filter_values.get("weapon_rarity")
            if rarity_data and isinstance(rarity_data, dict):
                value_types = rarity_data.get("value_types")
                if value_types and isinstance(value_types, list) and value_types:
                    enum_str = value_types[0].get("enum_string")
                    if enum_str and enum_str.isdigit():
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
                    key_for_check = re.sub(
                        r'\s+', ' ', key_clean).strip().lower().strip(":")
                    if key_for_check not in ALL_STANDARD_KEYS_LOWER:
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
        aggregated_data = {}

        # Etapa 1: Agregar os dados de todos os idiomas
        for lang, page_data in full_data.items():
            component = self._find_component_in_modules(page_data, 'ascension')
            if not component:
                continue

            parsed_data = self._parse_json_string(component.get('data', ''))
            parsed_list = parsed_data.get(
                'list', []) if isinstance(parsed_data, dict) else []

            for i, level_info in enumerate(parsed_list):
                level_key = i
                if level_key not in aggregated_data:
                    aggregated_data[level_key] = {
                        "level_name": {},
                        "combat_list_by_lang": {},
                        "materials_raw": []  # Inicializa como lista vazia
                    }
                aggregated_data[level_key]['level_name'][lang] = self._clean_html_tags(
                    level_info.get('key'))
                aggregated_data[level_key]['combat_list_by_lang'][lang] = level_info.get(
                    'combatList', [])

                # --- AQUI ESTÁ A CORREÇÃO ---
                # Se a lista de materiais para este idioma não estiver vazia E
                # nós ainda não tivermos encontrado nenhuma, salve esta.
                if level_info.get('materials') and not aggregated_data[level_key]['materials_raw']:
                    aggregated_data[level_key]['materials_raw'] = level_info.get(
                        'materials')

        # Etapa 2: Processar os dados agregados
        for level_key, data in aggregated_data.items():
            level_name = self._normalize_translations(
                data['level_name'], use_fallback_value=True)

            mats = await self._process_generic_materials(data['materials_raw'])
            if mats:
                materials.append({'level': level_name, 'materials': mats})

            if combat_lists_by_lang := data.get('combat_list_by_lang', {}):
                stats_list = []
                ref_lang_data = combat_lists_by_lang.get(
                    'en-us') or next(iter(combat_lists_by_lang.values()), [])

                if len(ref_lang_data) >= 2:
                    ref_headers = ref_lang_data[0].get('values', [])
                    ref_values = ref_lang_data[1].get('values', [])

                    if len(ref_headers) >= 2:
                        labels = {lang: lst[0]['values'][0] for lang, lst in combat_lists_by_lang.items(
                        ) if len(lst) > 0 and len(lst[0]['values']) > 0}
                        stats_list.append({
                            'label': self._normalize_translations(labels, use_fallback_value=True),
                            'preAscensionValue': ref_values[0] if ref_values and ref_values[0] != '-' else None,
                            'postAscensionValue': ref_values[1] if len(ref_values) > 1 and ref_values[1] != '-' else None
                        })

                    if len(ref_headers) >= 3:
                        labels = {lang: lst[0]['values'][2] for lang, lst in combat_lists_by_lang.items(
                        ) if len(lst) > 0 and len(lst[0]['values']) > 2}
                        stats_list.append({
                            'label': self._normalize_translations(labels, use_fallback_value=True),
                            'value': ref_values[2] if len(ref_values) > 2 and ref_values[2] != '-' else None
                        })

                if stats_list:
                    attributes.append(
                        {'level': level_name, 'stats': stats_list})

        return attributes, materials

    # --- FUNÇÃO PRINCIPAL DE PARSING DE ARMA ---

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
            "id": friendly_id,
            "wiki_id": wiki_id,
            "name": self._normalize_translations(name),
            "description": self._normalize_translations(description),
            "rarity": rarity,
            "type": weapon_type_values,
            "subStat": self._normalize_translations(sub_stat_translations),
            "passiveName": self._normalize_translations(passive_name),
            "passiveDescription": self._normalize_translations(passive_desc),
            "weaponIconUrl": weapon_icon,
            "ascensionMaterials": ascension_materials,
            "attributes": attributes
        }
        return weapon_info
