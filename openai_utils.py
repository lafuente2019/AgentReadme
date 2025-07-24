"""
Módulo openai_utils.py

Responsável por lidar com:
- Criação de embeddings (representações numéricas de textos)
- Cálculo de similaridade
- Montar e enviar prompts para o modelo de linguagem
"""

import math
from functools import lru_cache
from openai import OpenAI
from config import OPENAI_API_KEY, CHUNK_SIZE, TOP_K, EMBEDDING_MODEL, CHAT_MODEL

# Inicializa o cliente da OpenAI com a chave segura do .env
client = OpenAI(api_key=OPENAI_API_KEY)

def chunk_text(text: str, size: int = CHUNK_SIZE) -> list[str]:
    """
    Divide o texto em pedaços (chunks) menores para gerar embeddings,
    respeitando um tamanho máximo.

    Args:
        text (str): Texto completo (ex: README)
        size (int): Tamanho máximo de cada chunk

    Returns:
        list[str]: Lista de strings com trechos do texto
    """
    lines, chunks, cur = text.splitlines(keepends=True), [], ''
    for l in lines:
        if len(cur) + len(l) > size and cur:
            chunks.append(cur)
            cur = l
        else:
            cur += l
    if cur:
        chunks.append(cur)
    return chunks

@lru_cache(maxsize=32)
def build_readme_embeddings(full_name: str, readme_loader) -> list:
    """
    Constrói embeddings para cada pedaço do README de um repositório.

    Args:
        full_name (str): Nome completo do repositório.
        readme_loader (func): Função que carrega o conteúdo do README.

    Returns:
        list: Lista de tuplas (chunk_texto, embedding_vetor).
    """
    readme = readme_loader(full_name)
    chunks = chunk_text(readme)
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=chunks)
    return list(zip(chunks, [d.embedding for d in resp.data]))

def cosine(a, b):
    """
    Calcula a similaridade do cosseno entre dois vetores.

    Args:
        a (list[float]): Vetor A
        b (list[float]): Vetor B

    Returns:
        float: Valor entre -1 e 1 indicando a similaridade
    """
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def call_openai_retrieval(full_name: str, question: str, readme_loader) -> str:
    """
    Usa embeddings + similaridade para montar um contexto reduzido e perguntar ao modelo.

    Args:
        full_name (str): Nome do repositório
        question (str): Pergunta do usuário
        readme_loader (func): Função que carrega o README

    Returns:
        str: Resposta do modelo
    """
    # Embedding da pergunta
    q_emb = client.embeddings.create(model=EMBEDDING_MODEL, input=[question]).data[0].embedding
    embs = build_readme_embeddings(full_name, readme_loader)

    # Similaridade e seleção dos chunks mais relevantes
    scored = sorted(((cosine(q_emb, e), chunk) for chunk, e in embs), reverse=True)
    top_chunks = [chunk for _, chunk in scored[:TOP_K]]

    # Prompt com os chunks selecionados
    contexto = "\n\n---\n\n".join(top_chunks)
    prompt = f"Você é um consultor de projetos. Use o contexto abaixo para responder objetivamente.\n\n{contexto}\n\nPergunta:\n{question}"

    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0
    )
    return resp.choices[0].message.content.strip()
