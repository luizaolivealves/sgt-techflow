"""
Testes de Integração — API REST de Tarefas
Valida os endpoints HTTP usando o cliente de teste do Flask.
Testa o ciclo completo: criação, leitura, atualização e exclusão via HTTP.
"""

import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.app import criar_app
from src.models.tarefa import limpar_tarefas
from src.models.usuario import limpar_usuarios


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture
def cliente():
    """
    Cria um cliente de testes Flask com app em modo de teste.
    O estado é limpo antes e depois de cada teste.
    """
    app = criar_app()
    app.config["TESTING"] = True
    limpar_tarefas()
    limpar_usuarios()
    with app.test_client() as cliente:
        yield cliente
    limpar_tarefas()
    limpar_usuarios()


def post_json(cliente, url, dados):
    """Atalho para requisições POST com JSON."""
    return cliente.post(
        url,
        data=json.dumps(dados),
        content_type="application/json"
    )


def put_json(cliente, url, dados):
    """Atalho para requisições PUT com JSON."""
    return cliente.put(
        url,
        data=json.dumps(dados),
        content_type="application/json"
    )


# ── Testes — GET /tarefas ─────────────────────────────────────────────────────

def test_get_tarefas_lista_vazia(cliente):
    """GET /tarefas com nenhuma tarefa deve retornar lista vazia."""
    resp = cliente.get("/tarefas")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_tarefas_retorna_todas(cliente):
    """GET /tarefas deve retornar todas as tarefas cadastradas."""
    post_json(cliente, "/tarefas", {"titulo": "T1", "prioridade": "ALTA"})
    post_json(cliente, "/tarefas", {"titulo": "T2", "prioridade": "BAIXA"})
    resp = cliente.get("/tarefas")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_get_tarefas_filtro_por_status(cliente):
    """GET /tarefas?status=A_FAZER deve filtrar corretamente."""
    post_json(cliente, "/tarefas", {"titulo": "T1", "prioridade": "ALTA"})
    post_json(cliente, "/tarefas", {"titulo": "T2", "prioridade": "MEDIA"})
    resp = cliente.get("/tarefas?status=A_FAZER")
    assert resp.status_code == 200
    tarefas = resp.get_json()
    assert all(t["status"] == "A_FAZER" for t in tarefas)


# ── Testes — POST /tarefas ────────────────────────────────────────────────────

def test_post_tarefa_valida(cliente):
    """POST /tarefas com dados válidos deve criar a tarefa e retornar 201."""
    resp = post_json(cliente, "/tarefas", {
        "titulo": "Implementar login",
        "prioridade": "ALTA",
        "descricao": "Criar sistema de autenticação",
    })
    assert resp.status_code == 201
    dados = resp.get_json()
    assert dados["titulo"] == "Implementar login"
    assert dados["status"] == "A_FAZER"
    assert dados["id"] == 1


def test_post_tarefa_sem_titulo_retorna_400(cliente):
    """POST /tarefas sem título deve retornar 400 Bad Request."""
    resp = post_json(cliente, "/tarefas", {"prioridade": "ALTA"})
    assert resp.status_code == 400
    assert "erro" in resp.get_json()


def test_post_tarefa_prioridade_invalida_retorna_400(cliente):
    """POST /tarefas com prioridade inválida deve retornar 400."""
    resp = post_json(cliente, "/tarefas", {
        "titulo": "Tarefa X",
        "prioridade": "URGENTISSIMA"
    })
    assert resp.status_code == 400


def test_post_tarefa_sem_payload_retorna_400(cliente):
    """POST /tarefas sem corpo JSON deve retornar 400."""
    resp = cliente.post("/tarefas", content_type="application/json")
    assert resp.status_code == 400


# ── Testes — GET /tarefas/<id> ────────────────────────────────────────────────

def test_get_tarefa_por_id_existente(cliente):
    """GET /tarefas/<id> deve retornar a tarefa correta."""
    post_json(cliente, "/tarefas", {"titulo": "Tarefa Específica", "prioridade": "MEDIA"})
    resp = cliente.get("/tarefas/1")
    assert resp.status_code == 200
    assert resp.get_json()["titulo"] == "Tarefa Específica"


def test_get_tarefa_por_id_inexistente_retorna_404(cliente):
    """GET /tarefas/<id> com ID inexistente deve retornar 404."""
    resp = cliente.get("/tarefas/9999")
    assert resp.status_code == 404


# ── Testes — PUT /tarefas/<id> ────────────────────────────────────────────────

def test_put_tarefa_atualiza_status(cliente):
    """PUT /tarefas/<id> deve atualizar o status da tarefa."""
    post_json(cliente, "/tarefas", {"titulo": "Atualizar", "prioridade": "ALTA"})
    resp = put_json(cliente, "/tarefas/1", {"status": "EM_PROGRESSO"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "EM_PROGRESSO"


def test_put_tarefa_inexistente_retorna_404(cliente):
    """PUT /tarefas/<id> com ID inexistente deve retornar 404."""
    resp = put_json(cliente, "/tarefas/9999", {"titulo": "Novo"})
    assert resp.status_code == 404


# ── Testes — DELETE /tarefas/<id> ────────────────────────────────────────────

def test_delete_tarefa_existente(cliente):
    """DELETE /tarefas/<id> deve remover a tarefa e retornar 200."""
    post_json(cliente, "/tarefas", {"titulo": "Excluir", "prioridade": "BAIXA"})
    resp = cliente.delete("/tarefas/1")
    assert resp.status_code == 200
    # Confirma que foi removida
    assert cliente.get("/tarefas/1").status_code == 404


def test_delete_tarefa_inexistente_retorna_404(cliente):
    """DELETE /tarefas/<id> com ID inexistente deve retornar 404."""
    resp = cliente.delete("/tarefas/9999")
    assert resp.status_code == 404


# ── Testes — Rota raiz ────────────────────────────────────────────────────────

def test_get_index_retorna_info_sistema(cliente):
    """GET / deve retornar informações do sistema."""
    resp = cliente.get("/")
    assert resp.status_code == 200
    dados = resp.get_json()
    assert "sistema" in dados
    assert "endpoints" in dados
