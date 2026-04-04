"""
Modelo de Usuário — SGT (Sistema de Gerenciamento de Tarefas)
Gerencia cadastro, autenticação e controle de perfil dos usuários.
"""

import hashlib

# Banco de dados em memória (dicionário email → Usuario)
_usuarios: dict = {}


class Usuario:
    """
    Representa um usuário do sistema.

    Atributos:
        nome (str): Nome completo do usuário.
        email (str): E-mail único, usado como identificador de login.
        senha_hash (str): Hash SHA-256 da senha (nunca armazenamos a senha em texto puro).
        perfil (str): Nível de acesso — ADMIN ou USUARIO.
    """

    def __init__(self, nome: str, email: str, senha: str,
                 perfil: str = "USUARIO"):
        """
        Inicializa um usuário com validações básicas.

        Raises:
            ValueError: Se nome, e-mail ou senha forem inválidos.
        """
        if not nome or not nome.strip():
            raise ValueError("O nome do usuário não pode ser vazio.")
        if not email or "@" not in email:
            raise ValueError("E-mail inválido.")
        if not senha or len(senha) < 4:
            raise ValueError("A senha deve ter no mínimo 4 caracteres.")

        perfil = perfil.upper()
        if perfil not in {"ADMIN", "USUARIO"}:
            raise ValueError("Perfil inválido. Use ADMIN ou USUARIO.")

        self.nome: str = nome.strip()
        self.email: str = email.strip().lower()
        self.senha_hash: str = self._hash(senha)
        self.perfil: str = perfil

    @staticmethod
    def _hash(senha: str) -> str:
        """Gera hash SHA-256 da senha para armazenamento seguro."""
        return hashlib.sha256(senha.encode()).hexdigest()

    def verificar_senha(self, senha: str) -> bool:
        """
        Verifica se a senha fornecida confere com o hash armazenado.

        Returns:
            bool: True se a senha for correta.
        """
        return self.senha_hash == self._hash(senha)

    def to_dict(self) -> dict:
        """Retorna o usuário como dicionário (sem expor o hash da senha)."""
        return {
            "nome": self.nome,
            "email": self.email,
            "perfil": self.perfil,
        }

    def __repr__(self) -> str:
        return f"<Usuario email='{self.email}' perfil='{self.perfil}'>"


# ── Funções de repositório ────────────────────────────────────────────────────

def registrar_usuario(usuario: Usuario) -> Usuario:
    """
    Cadastra um novo usuário.

    Raises:
        ValueError: Se o e-mail já estiver cadastrado.
    """
    if usuario.email in _usuarios:
        raise ValueError(f"E-mail '{usuario.email}' já está cadastrado.")
    _usuarios[usuario.email] = usuario
    return usuario


def autenticar_usuario(email: str, senha: str):
    """
    Verifica as credenciais de login.

    Returns:
        Usuario: Objeto do usuário autenticado, ou None se inválido.
    """
    email = email.strip().lower()
    usuario = _usuarios.get(email)
    if usuario and usuario.verificar_senha(senha):
        return usuario
    return None


def buscar_usuario(email: str):
    """Retorna um usuário pelo e-mail, ou None se não encontrado."""
    return _usuarios.get(email.strip().lower())


def limpar_usuarios() -> None:
    """Remove todos os usuários (usado nos testes)."""
    _usuarios.clear()
