from dotenv import load_dotenv
import os

# Carrega variáveis do .env automaticamente
load_dotenv()

# ───────────────────────────────────────────────
# CONFIGURAÇÕES DOS TOKENS (GITHUB E OPENAI)
# ───────────────────────────────────────────────

# Lê do ambiente (.env ou variáveis exportadas no sistema)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validação para garantir que as variáveis foram definidas
assert GITHUB_TOKEN, "⚠️ Defina a variável GITHUB_TOKEN no seu ambiente ou .env"
assert OPENAI_API_KEY, "⚠️ Defina a variável OPENAI_API_KEY no seu ambiente ou .env"

# ───────────────────────────────────────────────
# PARÂMETROS DE FUNCIONAMENTO DO AGENTE
# ───────────────────────────────────────────────
CHUNK_SIZE = 8000            # Tamanho de cada pedaço para embeddings
TOP_K = 7                    # Quantidade de chunks mais relevantes selecionados


# Modelos utilizados
EMBEDDING_MODEL = "text-embedding-3-large"
CHAT_MODEL = "gpt-3.5-turbo"
