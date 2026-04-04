"""
Testes Unitários — Modelo Tarefa
Valida as regras de negócio do modelo Tarefa:
criação, validações, alteração de status e operações CRUD em memória.
"""

import pytest
import sys
import os

# Garante que o diretório raiz do projeto está no path do Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.tarefa import (
    Tarefa, criar_tarefa, listar_tarefas, buscar_tarefa_por_id,
    atualizar_tarefa, excluir_tarefa, limpar_tarefas
)


# ── Fixture: limpa o estado antes de cada teste ───────────────────────────────
@pytest.fixture(autouse=True)
def limpar():
    """Reseta o banco em memória antes de cada teste para isolamento."""
    limpar_tarefas()
    yield
    limpar_tarefas()


# ── Testes de criação ─────────────────────────────────────────────────────────

def test_criar_tarefa_valida():
    """Tarefa criada com dados válidos deve ter status inicial A_FAZER."""
    tarefa = Tarefa(titulo="Revisar relatório", prioridade="ALTA")
    assert tarefa.titulo == "Revisar relatório"
    assert tarefa.status == "A_FAZER"
    assert tarefa.prioridade == "ALTA"


def test_criar_tarefa_prioridade_minuscula():
    """Prioridade em minúsculo deve ser normalizada para maiúsculo."""
    tarefa = Tarefa(titulo="Deploy", prioridade="media")
    assert tarefa.prioridade == "MEDIA"


def test_criar_tarefa_sem_titulo_levanta_erro():
    """Título vazio deve levantar ValueError."""
    with pytest.raises(ValueError, match="título"):
        Tarefa(titulo="")


def test_criar_tarefa_titulo_espacos_levanta_erro():
    """Título com apenas espaços deve levantar ValueError."""
    with pytest.raises(ValueError):
        Tarefa(titulo="   ")


def test_criar_tarefa_prioridade_invalida_levanta_erro():
    """Prioridade desconhecida deve levantar ValueError."""
    with pytest.raises(ValueError, match="Prioridade inválida"):
        Tarefa(titulo="Tarefa X", prioridade="URGENTE")


def test_criar_tarefa_com_todos_os_campos():
    """Tarefa criada com todos os campos deve persistir corretamente."""
    tarefa = Tarefa(
        titulo="Configurar servidor",
        prioridade="ALTA",
        descricao="Instalar e configurar o servidor de produção",
        prazo="30/06/2026",
        usuario_email="dev@techflow.com",
    )
    assert tarefa.descricao == "Instalar e configurar o servidor de produção"
    assert tarefa.prazo == "30/06/2026"
    assert tarefa.usuario_email == "dev@techflow.com"


# ── Testes de status ──────────────────────────────────────────────────────────

def test_alterar_status_valido():
    """Status deve ser alterado corretamente para um valor válido."""
    tarefa = Tarefa(titulo="Deploy produção", prioridade="ALTA")
    tarefa.alterar_status("EM_PROGRESSO")
    assert tarefa.status == "EM_PROGRESSO"


def test_alterar_status_concluido():
    """Tarefa deve poder ser marcada como concluída."""
    tarefa = Tarefa(titulo="Testes unitários", prioridade="MEDIA")
    tarefa.alterar_status("CONCLUIDO")
    assert tarefa.status == "CONCLUIDO"


def test_alterar_status_invalido_levanta_erro():
    """Status desconhecido deve levantar ValueError."""
    tarefa = Tarefa(titulo="Tarefa Y", prioridade="BAIXA")
    with pytest.raises(ValueError, match="Status inválido"):
        tarefa.alterar_status("PAUSADO")


def test_alterar_status_minusculo_normalizado():
    """Status em minúsculo deve ser normalizado."""
    tarefa = Tarefa(titulo="Revisão", prioridade="MEDIA")
    tarefa.alterar_status("concluido")
    assert tarefa.status == "CONCLUIDO"


# ── Testes de CRUD em memória ─────────────────────────────────────────────────

def test_salvar_tarefa_atribui_id_unico():
    """Cada tarefa salva deve receber um ID único sequencial."""
    t1 = criar_tarefa(Tarefa(titulo="Tarefa 1", prioridade="ALTA"))
    t2 = criar_tarefa(Tarefa(titulo="Tarefa 2", prioridade="BAIXA"))
    assert t1.id == 1
    assert t2.id == 2


def test_listar_tarefas_retorna_todas():
    """listar_tarefas deve retornar todas as tarefas cadastradas."""
    criar_tarefa(Tarefa(titulo="A", prioridade="ALTA"))
    criar_tarefa(Tarefa(titulo="B", prioridade="MEDIA"))
    criar_tarefa(Tarefa(titulo="C", prioridade="BAIXA"))
    assert len(listar_tarefas()) == 3


def test_buscar_tarefa_por_id_existente():
    """Deve retornar a tarefa correta ao buscar por ID."""
    t = criar_tarefa(Tarefa(titulo="Buscar esta", prioridade="ALTA"))
    encontrada = buscar_tarefa_por_id(t.id)
    assert encontrada is not None
    assert encontrada.titulo == "Buscar esta"


def test_buscar_tarefa_por_id_inexistente():
    """Deve retornar None para ID que não existe."""
    assert buscar_tarefa_por_id(9999) is None


def test_atualizar_tarefa_titulo():
    """Deve atualizar o título de uma tarefa existente."""
    t = criar_tarefa(Tarefa(titulo="Título antigo", prioridade="MEDIA"))
    atualizar_tarefa(t.id, {"titulo": "Título novo"})
    assert buscar_tarefa_por_id(t.id).titulo == "Título novo"


def test_atualizar_tarefa_inexistente_retorna_none():
    """Atualizar ID inexistente deve retornar None."""
    resultado = atualizar_tarefa(9999, {"titulo": "X"})
    assert resultado is None


def test_excluir_tarefa_existente():
    """Deve excluir a tarefa e retornar True."""
    t = criar_tarefa(Tarefa(titulo="Excluir esta", prioridade="BAIXA"))
    resultado = excluir_tarefa(t.id)
    assert resultado is True
    assert buscar_tarefa_por_id(t.id) is None


def test_excluir_tarefa_inexistente_retorna_false():
    """Excluir ID inexistente deve retornar False."""
    assert excluir_tarefa(9999) is False


def test_to_dict_contem_campos_corretos():
    """to_dict deve conter todos os campos esperados."""
    t = criar_tarefa(Tarefa(titulo="Dict test", prioridade="ALTA",
                            usuario_email="user@test.com"))
    d = t.to_dict()
    assert "id" in d
    assert "titulo" in d
    assert "prioridade" in d
    assert "status" in d
    assert "criado_em" in d
    assert d["titulo"] == "Dict test"
