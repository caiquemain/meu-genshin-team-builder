import json
import os


def save_to_json_file(data, filename, directory=None):
    """Salva dados em um arquivo JSON."""
    if directory:
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
    else:
        filepath = filename

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Dados salvos em '{filepath}'")
    except Exception as e:
        print(f"Erro ao salvar arquivo '{filepath}': {e}")


def load_from_json_file(filename, directory=None):
    """Carrega dados de um arquivo JSON."""
    if directory:
        filepath = os.path.join(directory, filename)
    else:
        filepath = filename

    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Dados carregados de '{filepath}'.")
            return data
        except json.JSONDecodeError as e:
            print(
                f"Erro ao decodificar JSON de '{filepath}': {e}. O arquivo pode estar corrompido.")
            return None
        except Exception as e:
            print(f"Erro ao carregar arquivo '{filepath}': {e}")
            return None
    return None
