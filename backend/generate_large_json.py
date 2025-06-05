import json
import math

# Define o tamanho alvo em MB
TARGET_MB = 1
# Converte para bytes
TARGET_BYTES = TARGET_MB * 1024 * 1024

# Conteúdo base do JSON (seus dados de login)
base_data = {
    "username": "teste",
    "password": "senha123",
    "dummy_data": ""  # Este campo será preenchido para atingir o tamanho
}

# Converte o base_data (sem o dummy_data preenchido) para JSON e calcula o tamanho inicial
# Usamos uma string pequena para o dummy_data para ter uma base
temp_data_for_size_calc = {
    "username": "teste",
    "password": "senha123",
    "dummy_data": "a"
}
initial_json_string = json.dumps(temp_data_for_size_calc)
# Calcula o tamanho em bytes da string inicial, incluindo aspas e chaves do dummy_data
initial_size = len(initial_json_string.encode('utf-8'))

# Calcula o tamanho que o dummy_data precisa ter.
# Subtraímos o tamanho inicial e a diferença entre o len("a") e o len("")
# Aumentamos um pouco para compensar o overhead de aspas, etc.
required_padding_len = TARGET_BYTES - initial_size - \
    len('"dummy_data":""') + 10  # 10 para margem de segurança

# Cria a string de preenchimento
if required_padding_len < 0:
    required_padding_len = 0  # Garante que não é negativo

padding_string = 'a' * required_padding_len

# Adiciona a string de preenchimento ao seu dicionário principal
base_data["dummy_data"] = padding_string

# Gera o JSON final
final_json_string = json.dumps(base_data)

# Imprime o tamanho final para verificação
final_byte_size = len(final_json_string.encode('utf-8'))
print(
    f"Tamanho do JSON gerado: {final_byte_size / (1024 * 1024):.2f} MB ({final_byte_size} bytes)")

# Imprime o JSON para você copiar
print("\n--- Copie o JSON abaixo e cole no Postman ---")
print(final_json_string)
