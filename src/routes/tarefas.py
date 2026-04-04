"""
Rotas da API REST — Tarefas
Endpoints para operações CRUD sobre as tarefas do sistema.

GET    /tarefas         → lista todas as tarefas
GET    /tarefas/<id>    → retorna uma tarefa específica
POST   /tarefas         → cria uma nova tarefa
PUT    /tarefas/<id>    → atualiza uma tarefa existente
DELETE /tarefas/<id>    → remove uma tarefa
"""

from flask import Blueprint, request, jsonify
from src.models.tarefa import (
    Tarefa, criar_tarefa, listar_tarefas,
    buscar_tarefa_por_id, atualizar_tarefa, excluir_tarefa
)

# Blueprint agrupa todas as rotas de tarefas sob o prefixo /tarefas
tarefas_bp = Blueprint("tarefas", __name__, url_prefix="/tarefas")


@tarefas_bp.route("", methods=["GET"])
def get_tarefas():
    """
    Lista todas as tarefas cadastradas.
    Suporta filtro opcional por status: GET /tarefas?status=A_FAZER
    """
    status_filtro = request.args.get("status", "").upper()
    tarefas = listar_tarefas()

    # Aplica filtro por status se informado
    if status_filtro:
        tarefas = [t for t in tarefas if t.status == status_filtro]

    return jsonify([t.to_dict() for t in tarefas]), 200


@tarefas_bp.route("/<int:tarefa_id>", methods=["GET"])
def get_tarefa(tarefa_id):
    """Retorna os detalhes de uma tarefa específica pelo ID."""
    tarefa = buscar_tarefa_por_id(tarefa_id)
    if not tarefa:
        return jsonify({"erro": "Tarefa não encontrada."}), 404
    return jsonify(tarefa.to_dict()), 200


@tarefas_bp.route("", methods=["POST"])
def post_tarefa():
    """
    Cria uma nova tarefa.

    Corpo esperado (JSON):
        titulo      (obrigatório): Título da tarefa.
        prioridade  (opcional):    ALTA, MEDIA ou BAIXA (padrão: MEDIA).
        descricao   (opcional):    Descrição detalhada.
        prazo       (opcional):    Data no formato DD/MM/AAAA.
        usuario_email (opcional):  E-mail do responsável.
    """
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Payload JSON obrigatório."}), 400

    try:
        nova_tarefa = Tarefa(
            titulo=dados.get("titulo", ""),
            prioridade=dados.get("prioridade", "MEDIA"),
            descricao=dados.get("descricao", ""),
            prazo=dados.get("prazo", ""),
            usuario_email=dados.get("usuario_email", ""),
        )
        criar_tarefa(nova_tarefa)
        return jsonify(nova_tarefa.to_dict()), 201

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@tarefas_bp.route("/<int:tarefa_id>", methods=["PUT"])
def put_tarefa(tarefa_id):
    """
    Atualiza os campos de uma tarefa existente.
    Apenas os campos enviados no JSON serão modificados.
    """
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Payload JSON obrigatório."}), 400

    try:
        tarefa = atualizar_tarefa(tarefa_id, dados)
        if not tarefa:
            return jsonify({"erro": "Tarefa não encontrada."}), 404
        return jsonify(tarefa.to_dict()), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@tarefas_bp.route("/<int:tarefa_id>", methods=["DELETE"])
def delete_tarefa(tarefa_id):
    """Remove permanentemente uma tarefa pelo ID."""
    removida = excluir_tarefa(tarefa_id)
    if not removida:
        return jsonify({"erro": "Tarefa não encontrada."}), 404
    return jsonify({"mensagem": f"Tarefa {tarefa_id} removida com sucesso."}), 200
