# config.py

BASE_API_URL = "https://sg-wiki-api-static.hoyolab.com/hoyowiki/genshin/wapi/entry_page"

# Lista de idiomas para os quais queremos coletar dados e traduções
# ESTA É A LISTA COMPLETA E SERÁ USADA PARA TODAS AS TRADUÇÕES NO JSON DE SAÍDA.
SUPPORTED_LANGUAGES = [
    "pt-pt", "en-us", "ja-jp", "zh-cn", "ko-kr", "ru-ru",
    "de-de", "fr-fr", "es-es", "id-id", "th-th", "vi-vn", "zh-tw"
]

# Caminho para o arquivo JSON com a lista de todos os personagens
ALL_CHARACTERS_FILE = "data/all_genshin_characters.json"

# Mapeamento de *nomes das categorias* de material para suas traduções.
# Para idiomas que não possuem uma tradução explícita aqui, usaremos o valor em inglês (en).
MATERIAL_CATEGORY_NAMES = {
    "Common Currency": {
        "en-us": "Common Currency",
        "pt-pt": "Moeda Comum",
        "ja-jp": "共通通貨",
        # Adicionando fallbacks para outros idiomas para garantir que todos tenham um valor
        "zh-cn": "通用货币",
        "ko-kr": "공통 화폐",
        "ru-ru": "Обычная валюта",
        "de-de": "Allgemeine Währung",
        "fr-fr": "Monnaie courante",
        "es-es": "Moneda común",
        "id-id": "Mata Uang Umum",
        "th-th": "เงินทั่วไป",
        "vi-vn": "Tiền tệ phổ biến",
        "zh-tw": "通用貨幣"
    },
    "All Specialties": {
        "en-us": "All Specialties",
        "pt-pt": "Todas as Especialidades",
        "ja-jp": "全ての特産品",
        "zh-cn": "所有特产",
        "ko-kr": "모든 특산물",
        # Adaptei para ser mais genérico
        "ru-ru": "Все материалы для возвышения персонажей",
        "de-de": "Alle Spezialitäten",
        "fr-fr": "Toutes les spécialités",
        "es-es": "Todas las especialidades",
        "id-id": "Semua Spesialisasi",
        "th-th": "วัตถุดิบพิเศษทั้งหมด",
        "vi-vn": "Tất cả đặc sản",
        "zh-tw": "所有特產"
    },
    "Weapon Ascension Material": {
        "en-us": "Weapon Ascension Material",
        "pt-pt": "Material de Ascensão de Arma",
        "ja-jp": "武器突破素材",
        "zh-cn": "武器突破素材",
        "ko-kr": "무기 돌파 소재",
        "ru-ru": "Материалы возвышения оружия",
        "de-de": "Waffenaufstiegsmaterial",
        "fr-fr": "Matériau d'ascension d'arme",
        "es-es": "Material de ascensión de arma",
        "id-id": "Material Ascension Senjata",
        "th-th": "วัสดุเลื่อนขั้นอาวุธ",
        "vi-vn": "Nguyên liệu đột phá vũ khí",
        "zh-tw": "武器突破素材"
    },
    "Character Ascension Material": {
        "en-us": "Character Ascension Material",
        "pt-pt": "Material de Ascensão de Personagem",
        "ja-jp": "キャラクター突破素材",
        "zh-cn": "角色突破素材",
        "ko-kr": "캐릭터 돌파 소재",
        "ru-ru": "Материалы возвышения персонажей",
        "de-de": "Charakteraufstiegsmaterial",
        "fr-fr": "Matériau d'ascension de personnage",
        "es-es": "Material de ascensión de personaje",
        "id-id": "Material Ascension Karakter",
        "th-th": "วัสดุเลื่อนขั้นตัวละคร",
        "vi-vn": "Nguyên liệu đột phá nhân vật",
        "zh-tw": "角色突破素材"
    },
    "Weapon and Character Enhancement Material": {
        "en-us": "Weapon and Character Enhancement Material",
        "pt-pt": "Material de Fortalecimento de Arma e Personagem",
        "ja-jp": "武器とキャラクター強化素材",
        "zh-cn": "武器与角色培养素材",
        "ko-kr": "무기 및 캐릭터 육성 소재",
        "ru-ru": "Материалы развития оружия и персонажей",
        "de-de": "Waffen- und Charakterverbesserungsmaterial",
        "fr-fr": "Matériau d'amélioration d'arme et de personnage",
        "es-es": "Material de mejora de arma y personaje",
        "id-id": "Material Peningkatan Senjata dan Karakter",
        "th-th": "วัสดุเสริมพลังอาวุธและตัวละคร",
        "vi-vn": "Nguyên liệu bồi dưỡng vũ khí và nhân vật",
        "zh-tw": "武器與角色培養素材"
    },
    "Character Talent Material": {
        "en-us": "Character Talent Material",
        "pt-pt": "Material de Talento de Personagem",
        "ja-jp": "キャラクター天賦素材",
        "zh-cn": "角色天赋素材",
        "ko-kr": "캐릭터 특성 소재",
        "ru-ru": "Материалы талантов персонажей",
        "de-de": "Charaktertalentmaterial",
        "fr-fr": "Matériau d'aptitude de personnage",
        "es-es": "Material de talento de personaje",
        "id-id": "Material Talenta Karakter",
        "th-th": "วัสดุพรสวรรค์ตัวละคร",
        "vi-vn": "Nguyên liệu thiên phú nhân vật",
        "zh-tw": "角色天賦素材"
    }
}

DEFAULT_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    # Este pode variar para cada requisição de idioma
    'accept-language': 'pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es;q=0.5',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://wiki.hoyolab.com',
    'priority': 'u=1, i',
    'referer': 'https://wiki.hoyolab.com/',
    'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
    'x-rpc-wiki_app': 'genshin',
}
