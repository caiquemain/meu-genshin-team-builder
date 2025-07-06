import os
import json
import asyncio
import aiohttp
import config
import re


async def download_image(session, remote_url, local_img_path):
    """Função auxiliar para baixar uma única imagem, garantindo que a pasta exista."""
    try:
        # Pula o download APENAS se o arquivo já existir no disco.
        if os.path.exists(local_img_path):
            return True

        async with session.get(remote_url) as response:
            if response.status == 200:
                content = await response.read()
                os.makedirs(os.path.dirname(local_img_path), exist_ok=True)
                with open(local_img_path, 'wb') as f:
                    f.write(content)
                print(f"  -> Sucesso: {os.path.relpath(local_img_path)}")
                return True
            else:
                print(
                    f"  -> FALHA ao baixar {remote_url}. Status: {response.status}")
                return False
    except Exception as e:
        print(f"  -> ERRO ao baixar/salvar {remote_url}: {e}")
        return False


async def process_character_file(session, char_filepath):
    """Processa um único arquivo de personagem para baixar todas as suas imagens para uma pasta dedicada."""
    try:
        with open(char_filepath, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            char_id = data.get('id')
            if not char_id:
                return

            print(f"Processando imagens para: {char_id}...")
            was_modified = False

            character_image_folder = os.path.join(
                config.CHARACTERS_IMAGES_DIR, char_id)

            def get_paths(url, filename):
                ext = os.path.splitext(url.split('?')[0])[1] or '.png'
                full_path = os.path.join(
                    character_image_folder, f"{filename}{ext}")
                relative_path = os.path.join(
                    'images', char_id, f"{filename}{ext}").replace('\\', '/')
                return full_path, relative_path

            download_jobs = {}

            # --- LÓGICA DE VERIFICAÇÃO ATUALIZADA ---
            def add_job(obj, key, url, filename_base):
                if not url or not url.startswith('http'):
                    return

                full_path, rel_path = get_paths(url, filename_base)

                # A condição chave: só adiciona o trabalho se o arquivo NÃO existir no disco
                if not os.path.exists(full_path):
                    download_jobs[full_path] = (obj, key, url, rel_path)
                # Garante que o campo no JSON esteja correto mesmo se o arquivo já existir
                elif obj.get(key) != rel_path:
                    obj[key] = rel_path
                    nonlocal was_modified
                    was_modified = True

            # Adiciona Ícones Principais
            add_job(data, 'localCharacterIconUrl',
                    data.get('characterIconUrl'), "icon")
            add_job(data, 'localElementIconUrl', data.get(
                'elementIconUrl'), "element_icon")

            # Adiciona Constelações
            for i, const in enumerate(data.get('constellations', [])):
                add_job(const, 'localIcon', const.get(
                    'iconUrl'), f"constellation_{i+1}")

            # Adiciona Talentos
            talent_name_map = {
                "Normal Attack": "talent_normal_attack", "Elemental Skill": "talent_elemental_skill",
                "Elemental Burst": "talent_elemental_burst", "1st Ascension Passive": "talent_passive_1",
                "4th Ascension Passive": "talent_passive_4", "Utility Passive": "talent_utility_passive",
            }
            for i, talent in enumerate(data.get('talents', [])):
                talent_type = talent.get('type', f'other_{i}')
                filename_base = talent_name_map.get(talent_type, talent_type)
                add_job(talent, 'localIcon', talent.get(
                    'iconUrl'), filename_base)

            if not download_jobs and not was_modified:
                return  # Nenhum trabalho a fazer para este personagem

            # Executa os downloads necessários
            for full_path, (obj_update, key, remote_url, rel_path) in download_jobs.items():
                if await download_image(session, remote_url, full_path):
                    obj_update[key] = rel_path
                    was_modified = True

            if was_modified:
                f.seek(0)
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.truncate()
                print(
                    f"  -> Arquivo '{os.path.basename(char_filepath)}' atualizado.")

    except Exception as e:
        print(
            f"ERRO GERAL ao processar o arquivo {os.path.basename(char_filepath)}: {e}")


async def main():
    print("--- Script de Download de Imagens de Personagens (v3 - Robusto) ---")
    os.makedirs(config.CHARACTERS_IMAGES_DIR, exist_ok=True)

    if not os.path.isdir(config.CHARACTERS_OUTPUT_DIR):
        print(
            f"ERRO: Diretório '{config.CHARACTERS_OUTPUT_DIR}' não encontrado.")
        return

    tasks = []
    async with aiohttp.ClientSession() as session:
        for filename in os.listdir(config.CHARACTERS_OUTPUT_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(config.CHARACTERS_OUTPUT_DIR, filename)
                tasks.append(process_character_file(session, filepath))

        await asyncio.gather(*tasks)

    print("\nProcesso de download de imagens de personagens concluído.")

if __name__ == '__main__':
    asyncio.run(main())
