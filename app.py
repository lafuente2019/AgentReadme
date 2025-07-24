"""
app.py

Este é o ponto principal do projeto. Ele:
- Inicializa o Flask
- Define a rota principal "/"
- Renderiza a página HTML com o formulário
- Ao receber POST, processa o README e chama o OpenAI via RAG
"""

from flask import Flask, render_template, request, flash
from github_utils import carregar_readme, get_user_repos
from openai_utils import call_openai_retrieval
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Segurança nos cookies

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Rota principal da aplicação:

    - GET: Exibe o formulário com os repositórios
    - POST: Processa a pergunta e retorna resposta baseada em RAG
    """
    # Cache da lista de repositórios do GitHub
    if not hasattr(app, 'repos_cache'):
        app.repos_cache = get_user_repos()
    repos = app.repos_cache

    answer = selected = question = None

    if request.method == 'POST':
        selected = request.form['repo']
        question = request.form['question'].strip()

        try:
            answer = call_openai_retrieval(
                full_name=selected,
                question=question,
                readme_loader=carregar_readme
            )
        except Exception as e:
            flash(f"Erro: {e}")

    return render_template('index.html', repos=repos, selected=selected, question=question, answer=answer)

if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv('PORT', 5000)))
