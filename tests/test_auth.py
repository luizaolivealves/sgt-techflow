"""
Testes Unitários — Autenticação de Usuários
Valida cadastro, login e regras de segurança do modelo Usuario.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.usuario import (
    Usuario, registrar_usuario, autenticar_usuario, limpar_usuarios
)


# ── Fixture ───────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def limpar():
    """Reseta os usuários antes de cada teste."""
    limpar_usuarios()
    yield
    limpar_usuarios()


# ── Testes de criação de usuário ──────────────────────────────────────────────

def test_criar_usuario_valido():
    """Usuário com dados válidos deve ser criado com perfil padrão USUARIO."""
    u = Usuario(nome="Ana Lima", email="ana@email.com", senha="1234")
    assert u.nome == "Ana Lima"
    assert u.email == "ana@email.com"
    assert u.perfil == "USUARIO"


def test_senha_nunca_armazenada_em_texto_puro():
    """A senha não deve ser armazenada como texto — apenas como hash."""
    u = Usuario(nome="Carlos", email="carlos@email.com", senha="senha123")
    assert u.senha_hash != "senha123"
    assert len(u.senha_hash) == 64  # SHA-256 gera 64 caracteres hex


def test_criar_usuario_sem_nome_levanta_erro():
    """Nome vazio deve levantar ValueError."""
    with pytest.raises(ValueError, match="nome"):
        Usuario(nome="", email="x@email.com", senha="1234")


def test_criar_usuario_email_invalido_levanta_erro():
    """E-mail sem '@' deve levantar ValueError."""
    with pytest.raises(ValueError, match="E-mail"):
        Usuario(nome="Test", email="emailsemarrobacom", senha="1234")


def test_criar_usuario_senha_curta_levanta_erro():
    """Senha com menos de 4 caracteres deve levantar ValueError."""
    with pytest.raises(ValueError, match="senha"):
        Usuario(nome="Test", email="t@t.com", senha="123")


def test_criar_usuario_perfil_invalido_levanta_erro():
    """Perfil desconhecido deve levantar ValueError."""
    with pytest.raises(ValueError, match="Perfil"):
        Usuario(nome="Test", email="t@t.com", senha="1234", perfil="SUPER")


# ── Testes de autenticação ────────────────────────────────────────────────────

def test_autenticar_com_credenciais_validas():
    """Login com e-mail e senha corretos deve retornar o usuário."""
    u = Usuario(nome="João", email="joao@email.com", senha="segura99")
    registrar_usuario(u)
    resultado = autenticar_usuario("joao@email.com", "segura99")
    assert resultado is not None
    assert resultado.email == "joao@email.com"


def test_autenticar_com_senha_errada_retorna_none():
    """Login com senha incorreta deve retornar None."""
    u = Usuario(nome="Maria", email="maria@email.com", senha="correta")
    registrar_usuario(u)
    resultado = autenticar_usuario("maria@email.com", "errada")
    assert resultado is None


def test_autenticar_email_inexistente_retorna_none():
    """Login com e-mail não cadastrado deve retornar None."""
    resultado = autenticar_usuario("ninguem@email.com", "qualquer")
    assert resultado is None


def test_email_normalizado_para_minusculo():
    """E-mail deve ser normalizado para letras minúsculas."""
    u = Usuario(nome="Pedro", email="Pedro@EMAIL.COM", senha="1234")
    registrar_usuario(u)
    resultado = autenticar_usuario("pedro@email.com", "1234")
    assert resultado is not None


# ── Testes de registro ────────────────────────────────────────────────────────

def test_registrar_email_duplicado_levanta_erro():
    """Dois usuários com o mesmo e-mail não devem ser permitidos."""
    u1 = Usuario(nome="User1", email="dup@email.com", senha="1234")
    u2 = Usuario(nome="User2", email="dup@email.com", senha="5678")
    registrar_usuario(u1)
    with pytest.raises(ValueError, match="já está cadastrado"):
        registrar_usuario(u2)


def test_to_dict_nao_expoe_senha_hash():
    """to_dict não deve incluir o campo senha_hash por segurança."""
    u = Usuario(nome="Seguro", email="seg@email.com", senha="1234")
    d = u.to_dict()
    assert "senha_hash" not in d
    assert "nome" in d
    assert "email" in d
    assert "perfil" in d
