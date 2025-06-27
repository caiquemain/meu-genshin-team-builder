# api_client.py (versão corrigida)
import aiohttp
import asyncio
from config import BASE_API_URL, DEFAULT_HEADERS, SUPPORTED_LANGUAGES


class APIClient:
    def __init__(self, cookie_string=None):
        self.headers = DEFAULT_HEADERS.copy()
        if cookie_string:
            self.headers['Cookie'] = cookie_string

    async def fetch_page_data(self, session, entry_page_id: str, lang: str) -> dict:
        """
        Faz uma requisição assíncrona para a página de um item e retorna o JSON.
        """
        url = f"{BASE_API_URL}?entry_page_id={entry_page_id}"
        request_headers = self.headers.copy()
        request_headers['x-rpc-language'] = lang
        request_headers['accept-language'] = f"{lang},{lang.split('-')[0]};q=0.9,en-US;q=0.8,en;q=0.7"

        try:
            async with session.get(url, headers=request_headers, timeout=15) as response:
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError:
            print(f"Timeout Error for {entry_page_id} in {lang}")
        except aiohttp.ClientError as e:
            print(f"Aiohttp Error for {entry_page_id} in {lang}: {e}")
        return {}

    async def fetch_item_translations(self, item_id: str) -> dict:
        """
        Busca as traduções de um item em todos os idiomas suportados de forma assíncrona.
        """
        translations = {}
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_page_data(session, item_id, lang)
                     for lang in SUPPORTED_LANGUAGES]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, lang in enumerate(SUPPORTED_LANGUAGES):
                item_data = results[i]
                if isinstance(item_data, dict) and item_data.get('retcode') == 0 and item_data.get('data', {}).get('page'):
                    item_name = item_data['data']['page'].get('name')
                    if item_name:
                        translations[lang] = item_name
        return translations

    # CORREÇÃO: A função agora está DENTRO da classe APIClient, com a indentação correta.
    async def post_page_list(self, session, url: str, payload: dict) -> dict:
        """
        Faz uma requisição POST assíncrona para a API de lista e retorna o JSON.
        """
        try:
            async with session.post(url, headers=self.headers, json=payload, timeout=20) as response:
                response.raise_for_status()
                return await response.json()
        except asyncio.TimeoutError:
            print(f"Timeout Error for POST request to {url}")
        except aiohttp.ClientError as e:
            print(f"Aiohttp Error for POST request to {url}: {e}")
        return {}
