import os
import json
import asyncio
import aiohttp
import config


async def download_and_update_weapon(session, weapon_filepath):
    """
    Baixa o ícone principal de uma arma, se necessário, e adiciona um campo
    'localIconUrl' ao seu arquivo JSON, preservando o 'weaponIconUrl' original.
    """
    try:
        # Abre o arquivo para leitura e depois para escrita
        with open(weapon_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        remote_url = data.get('weaponIconUrl')
        slug_id = data.get('id')

        # 1. Validação: Pula se não houver slug_id ou URL remoto
        if not slug_id or not remote_url or not remote_url.startswith('http'):
            return

        # 2. Define os caminhos e nomes dos arquivos
        file_extension = os.path.splitext(
            remote_url.split('?')[0])[1] or '.png'
        local_filename = f"{slug_id}{file_extension}"
        local_filepath_img = os.path.join(
            config.WEAPONS_IMAGES_DIR, local_filename)
        relative_path_for_json = f"images/{local_filename}"

        # 3. Verifica se o trabalho já foi feito para evitar re-download
        if data.get('localIconUrl') == relative_path_for_json and os.path.exists(local_filepath_img):
            return

        print(f"Baixando ícone para a arma: {slug_id}...")
        async with session.get(remote_url) as response:
            if response.status == 200:
                content = await response.read()
                with open(local_filepath_img, 'wb') as img_file:
                    img_file.write(content)

                # 4. Atualiza o JSON adicionando o novo campo
                data['localIconUrl'] = relative_path_for_json

                with open(weapon_filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                print(
                    f"  -> Sucesso: '{slug_id}' atualizado com o campo localIconUrl.")
            else:
                print(
                    f"  -> FALHA ao baixar {slug_id}. Status: {response.status}")

    except Exception as e:
        print(
            f"ERRO ao processar o arquivo {os.path.basename(weapon_filepath)}: {e}")


async def main():
    """Função principal para orquestrar o download de todas as imagens de armas."""
    print("--- Script de Download de Imagens de Armas ---")

    os.makedirs(config.WEAPONS_IMAGES_DIR, exist_ok=True)

    if not os.path.isdir(config.WEAPONS_OUTPUT_DIR):
        print(f"ERRO: Diretório '{config.WEAPONS_OUTPUT_DIR}' não encontrado.")
        return

    tasks = []
    async with aiohttp.ClientSession() as session:
        for filename in os.listdir(config.WEAPONS_OUTPUT_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(config.WEAPONS_OUTPUT_DIR, filename)
                tasks.append(download_and_update_weapon(session, filepath))

        if not tasks:
            print("Nenhum arquivo JSON de arma encontrado para processar.")
            return

        await asyncio.gather(*tasks)

    print("\nProcesso de download de imagens de armas concluído.")

if __name__ == '__main__':
    asyncio.run(main())
