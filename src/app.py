"""
SGT — Sistema de Gerenciamento de Tarefas
TechFlow Solutions · Engenharia de Software · UniFECAF

Ponto de entrada da aplicação Flask.
Registra os blueprints de rotas e inicia o servidor de desenvolvimento.

Para executar:
    python src/app.py

Acesse: http://localhost:5000
"""

from flask import Flask, jsonify
from src.routes.tarefas import tarefas_bp
from src.routes.auth import auth_bp


def criar_app() -> Flask:
    """
    Fábrica de aplicação Flask.
    Centraliza a criação e configuração do app,
    facilitando a instanciação em testes automatizados.

    Returns:
        Flask: Instância configurada da aplicação.
    """
    app = Flask(__name__)

    # Chave secreta para sessões (em produção, usar variável de ambiente)
    app.config["SECRET_KEY"] = "sgt-techflow-secret-2026"
    app.config["JSON_AS_ASCII"] = False  # Suporte a caracteres UTF-8

    # Registra os blueprints (grupos de rotas)
    app.register_blueprint(tarefas_bp)
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        """Rota raiz — apresenta os endpoints disponíveis."""
        return jsonify({
            "sistema": "SGT — Sistema de Gerenciamento de Tarefas",
            "versao": "1.0.0",
            "empresa": "TechFlow Solutions",
            "endpoints": {
                "tarefas": {
                    "GET    /tarefas": "Lista todas as tarefas",
                    "GET    /tarefas/<id>": "Retorna uma tarefa",
                    "POST   /tarefas": "Cria uma nova tarefa",
                    "PUT    /tarefas/<id>": "Atualiza uma tarefa",
                    "DELETE /tarefas/<id>": "Remove uma tarefa",
                },
                "autenticacao": {
                    "POST /auth/registro": "Cadastra novo usuário",
                    "POST /auth/login": "Realiza login",
                },
            }
        }), 200

    @app.errorhandler(404)
    def nao_encontrado(e):
        """Trata rotas não existentes com resposta JSON padronizada."""
        return jsonify({"erro": "Rota não encontrada."}), 404

    @app.errorhandler(405)
    def metodo_nao_permitido(e):
        """Trata métodos HTTP não suportados."""
        return jsonify({"erro": "Método não permitido."}), 405

    return app


if __name__ == "__main__":
    app = criar_app()
    print("=" * 50)
    print("  SGT — Sistema de Gerenciamento de Tarefas")
    print("  TechFlow Solutions  |  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
