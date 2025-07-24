"""
Módulo github_utils.py

Responsável por fazer toda a comunicação com o GitHub:
- Obter lista de repositórios do usuário
- Carregar conteúdo do README de um repositório
"""

from github import Github, GithubException
from functools import lru_cache
from config import GITHUB_TOKEN

# Inicializa o cliente do GitHub usando o token
gh = Github(GITHUB_TOKEN)

@lru_cache(maxsize=32)
def carregar_readme(full_name: str) -> str:
    """
    Carrega o conteúdo do README.md de um repositório específico do GitHub.

    Args:
        full_name (str): Nome completo do repositório (ex: "usuario/repositorio")

    Returns:
        str: Conteúdo do README em texto.

    Raises:
        FileNotFoundError: Se o README não for encontrado no repositório.
    """
    repo = gh.get_repo(full_name)
    try:
        # Tenta pegar o README principal do repositório
        return repo.get_readme().decoded_content.decode('utf-8')
    except GithubException:
        # Se não tiver o README padrão, procura arquivos parecidos na raiz
        for item in repo.get_contents(''):
            if item.type == 'file' and item.name.lower().startswith('readme'):
                return item.decoded_content.decode('utf-8')
    raise FileNotFoundError('README não encontrado.')

def get_user_repos():
    """
    Retorna a lista de repositórios do usuário autenticado no GitHub.

    Returns:
        list: Lista de objetos de repositórios do GitHub.
    """
    return list(gh.get_user().get_repos())
