"""
Testes Unitários — Serviço de Notificações por E-mail
Valida o envio de e-mails usando Mock do cliente SMTP,
sem realizar conexões reais de rede.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.tarefa import Tarefa, limpar_tarefas
from src.services.notificacao import NotificacaoService


# ── Fixture: tarefa de exemplo ────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def limpar():
    limpar_tarefas()
    yield
    limpar_tarefas()


@pytest.fixture
def tarefa_com_prazo_proximo():
    """Cria uma tarefa com prazo em formato passado para simular prazo próximo."""
    t = Tarefa(
        titulo="Entregar relatório",
        prioridade="ALTA",
        prazo="01/01/2024",  # Data passada → prazo próximo/vencido
        usuario_email="responsavel@techflow.com"
    )
    t.id = 1
    return t


@pytest.fixture
def tarefa_sem_email():
    """Cria uma tarefa sem e-mail de responsável."""
    t = Tarefa(titulo="Tarefa sem e-mail", prioridade="MEDIA")
    t.id = 2
    return t


@pytest.fixture
def smtp_mock():
    """Retorna um objeto Mock que simula o cliente SMTP."""
    mock = MagicMock()
    mock.sendmail.return_value = {}  # SMTP.sendmail retorna dict vazio em sucesso
    return mock


# ── Testes — notificar_prazo_proximo ─────────────────────────────────────────

def test_notifica_prazo_proximo_envia_email(tarefa_com_prazo_proximo, smtp_mock):
    """Deve enviar e-mail quando o prazo estiver próximo ou vencido."""
    servico = NotificacaoService(smtp_client=smtp_mock)
    resultado = servico.notificar_prazo_proximo(tarefa_com_prazo_proximo)
    assert resultado is True
    assert smtp_mock.sendmail.called


def test_nao_notifica_prazo_sem_email(tarefa_sem_email, smtp_mock):
    """Não deve enviar e-mail quando a tarefa não tem responsável configurado."""
    servico = NotificacaoService(smtp_client=smtp_mock)
    resultado = servico.notificar_prazo_proximo(tarefa_sem_email)
    assert resultado is False
    assert not smtp_mock.sendmail.called


def test_nao_notifica_tarefa_sem_prazo(smtp_mock):
    """Não deve enviar e-mail quando a tarefa não tem prazo definido."""
    tarefa = Tarefa(titulo="Sem prazo", prioridade="MEDIA",
                    usuario_email="user@test.com")
    servico = NotificacaoService(smtp_client=smtp_mock)
    resultado = servico.notificar_prazo_proximo(tarefa)
    assert resultado is False


def test_nao_notifica_prazo_distante(smtp_mock):
    """Não deve enviar e-mail quando o prazo está a mais de 48 horas."""
    tarefa = Tarefa(titulo="Prazo longe", prioridade="BAIXA",
                    prazo="31/12/2099",  # Data muito futura
                    usuario_email="user@test.com")
    servico = NotificacaoService(smtp_client=smtp_mock)
    resultado = servico.notificar_prazo_proximo(tarefa)
    assert resultado is False


def test_nao_notifica_prazo_formato_invalido(smtp_mock):
    """Prazo em formato incorreto não deve disparar envio."""
    tarefa = Tarefa(titulo="Formato errado", prioridade="MEDIA",
                    prazo="2024/12/31",  # Formato incorreto
                    usuario_email="user@test.com")
    servico = NotificacaoService(smtp_client=smtp_mock)
    resultado = servico.notificar_prazo_proximo(tarefa)
    assert resultado is False


# ── Testes — notificar_mudanca_status ────────────────────────────────────────

def test_notifica_mudanca_status_outro_usuario(smtp_mock):
    """Deve notificar quando outro usuário altera o status da tarefa."""
    tarefa = Tarefa(titulo="Revisão de código", prioridade="ALTA",
                    usuario_email="dev@techflow.com")
    tarefa.alterar_status("EM_PROGRESSO")
    servico = NotificacaoService(smtp_client=smtp_mock)
    resultado = servico.notificar_mudanca_status(
        tarefa,
        status_anterior="A_FAZER",
        alterado_por="gestor@techflow.com"  # E-mail diferente do responsável
    )
    assert resultado is True
    assert smtp_mock.sendmail.called


def test_nao_notifica_quando_proprio_responsavel_altera(smtp_mock):
    """Não deve notificar quando o próprio responsável altera o status."""
    tarefa = Tarefa(titulo="Minha tarefa", prioridade="MEDIA",
                    usuario_email="eu@techflow.com")
    tarefa.alterar_status("EM_PROGRESSO")
    servico = NotificacaoService(smtp_client=smtp_mock)
    resultado = servico.notificar_mudanca_status(
        tarefa,
        status_anterior="A_FAZER",
        alterado_por="eu@techflow.com"  # Mesmo e-mail → não notifica
    )
    assert resultado is False
    assert not smtp_mock.sendmail.called


def test_nao_notifica_mudanca_sem_email_responsavel(smtp_mock):
    """Não deve notificar quando a tarefa não tem responsável."""
    tarefa = Tarefa(titulo="Sem responsável", prioridade="BAIXA")
    tarefa.alterar_status("CONCLUIDO")
    servico = NotificacaoService(smtp_client=smtp_mock)
    resultado = servico.notificar_mudanca_status(
        tarefa,
        status_anterior="EM_PROGRESSO",
        alterado_por="gestor@techflow.com"
    )
    assert resultado is False


def test_falha_smtp_retorna_false(tarefa_com_prazo_proximo):
    """Erro no servidor SMTP deve retornar False sem lançar exceção."""
    smtp_com_erro = MagicMock()
    smtp_com_erro.sendmail.side_effect = Exception("Conexão recusada")
    servico = NotificacaoService(smtp_client=smtp_com_erro)
    resultado = servico.notificar_prazo_proximo(tarefa_com_prazo_proximo)
    assert resultado is False  # Deve retornar False, não lançar exceção
