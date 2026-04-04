"""
Modelo de Tarefa — SGT (Sistema de Gerenciamento de Tarefas)
Contém a classe Tarefa com atributos, validações e operações CRUD em memória.
"""

from datetime import datetime

# Valores permitidos para prioridade e status
PRIORIDADES_VALIDAS = {"ALTA", "MEDIA", "BAIXA"}
STATUS_VALIDOS = {"A_FAZER", "EM_PROGRESSO", "CONCLUIDO"}

# Banco de dados em memória (lista de tarefas)
_tarefas: list = []
_proximo_id: int = 1


class Tarefa:
    """
    Representa uma tarefa do sistema de gerenciamento.

    Atributos:
        id (int): Identificador único gerado automaticamente.
        titulo (str): Título obrigatório da tarefa (não pode ser vazio).
        descricao (str): Descrição opcional com detalhes da tarefa.
        prioridade (str): Nível de prioridade — ALTA, MEDIA ou BAIXA.
        status (str): Estado atual — A_FAZER, EM_PROGRESSO ou CONCLUIDO.
        prazo (str): Data limite no formato DD/MM/AAAA (opcional).
        usuario_email (str): E-mail do responsável pela tarefa.
        criado_em (str): Data/hora de criação (preenchida automaticamente).
    """

    def __init__(self, titulo: str, prioridade: str = "MEDIA",
                 descricao: str = "", prazo: str = "",
                 usuario_email: str = ""):
        """
        Inicializa uma nova tarefa com validações obrigatórias.

        Raises:
            ValueError: Se o título for vazio ou a prioridade for inválida.
        """
        # Valida título obrigatório
        if not titulo or not titulo.strip():
            raise ValueError("O título da tarefa não pode ser vazio.")

        # Valida prioridade
        prioridade = prioridade.upper()
        if prioridade not in PRIORIDADES_VALIDAS:
            raise ValueError(
                f"Prioridade inválida: '{prioridade}'. "
                f"Use: {PRIORIDADES_VALIDAS}"
            )

        self.id: int = 0  # Será atribuído ao salvar
        self.titulo: str = titulo.strip()
        self.descricao: str = descricao.strip()
        self.prioridade: str = prioridade
        self.status: str = "A_FAZER"  # Status inicial padrão
        self.prazo: str = prazo.strip()
        self.usuario_email: str = usuario_email.strip()
        self.criado_em: str = datetime.now().strftime("%d/%m/%Y %H:%M")

    def alterar_status(self, novo_status: str) -> None:
        """
        Altera o status da tarefa para um valor válido.

        Args:
            novo_status (str): Novo status — A_FAZER, EM_PROGRESSO ou CONCLUIDO.

        Raises:
            ValueError: Se o status fornecido for inválido.
        """
        novo_status = novo_status.upper()
        if novo_status not in STATUS_VALIDOS:
            raise ValueError(
                f"Status inválido: '{novo_status}'. "
                f"Use: {STATUS_VALIDOS}"
            )
        self.status = novo_status

    def to_dict(self) -> dict:
        """Retorna a tarefa como dicionário (útil para serialização JSON)."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "prioridade": self.prioridade,
            "status": self.status,
            "prazo": self.prazo,
            "usuario_email": self.usuario_email,
            "criado_em": self.criado_em,
        }

    def __repr__(self) -> str:
        return (
            f"<Tarefa id={self.id} titulo='{self.titulo}' "
            f"status='{self.status}' prioridade='{self.prioridade}'>"
        )


# ── Funções de repositório (operações CRUD em memória) ────────────────────────

def criar_tarefa(tarefa: Tarefa) -> Tarefa:
    """Salva uma nova tarefa na lista e atribui um ID único."""
    global _proximo_id
    tarefa.id = _proximo_id
    _proximo_id += 1
    _tarefas.append(tarefa)
    return tarefa


def listar_tarefas() -> list:
    """Retorna todas as tarefas cadastradas."""
    return list(_tarefas)


def buscar_tarefa_por_id(tarefa_id: int):
    """
    Busca uma tarefa pelo ID.

    Returns:
        Tarefa: Objeto encontrado, ou None se não existir.
    """
    for t in _tarefas:
        if t.id == tarefa_id:
            return t
    return None


def atualizar_tarefa(tarefa_id: int, dados: dict):
    """
    Atualiza os campos de uma tarefa existente.

    Args:
        tarefa_id (int): ID da tarefa a atualizar.
        dados (dict): Campos a modificar (titulo, descricao, prioridade, status, prazo).

    Returns:
        Tarefa: Tarefa atualizada, ou None se não encontrada.

    Raises:
        ValueError: Se prioridade ou status forem inválidos.
    """
    tarefa = buscar_tarefa_por_id(tarefa_id)
    if not tarefa:
        return None

    if "titulo" in dados:
        novo_titulo = dados["titulo"].strip()
        if not novo_titulo:
            raise ValueError("O título não pode ser vazio.")
        tarefa.titulo = novo_titulo

    if "descricao" in dados:
        tarefa.descricao = dados["descricao"].strip()

    if "prioridade" in dados:
        nova_prioridade = dados["prioridade"].upper()
        if nova_prioridade not in PRIORIDADES_VALIDAS:
            raise ValueError(f"Prioridade inválida: '{nova_prioridade}'.")
        tarefa.prioridade = nova_prioridade

    if "status" in dados:
        tarefa.alterar_status(dados["status"])

    if "prazo" in dados:
        tarefa.prazo = dados["prazo"].strip()

    return tarefa


def excluir_tarefa(tarefa_id: int) -> bool:
    """
    Remove uma tarefa da lista pelo ID.

    Returns:
        bool: True se excluída com sucesso, False se não encontrada.
    """
    global _tarefas
    antes = len(_tarefas)
    _tarefas = [t for t in _tarefas if t.id != tarefa_id]
    return len(_tarefas) < antes


def limpar_tarefas() -> None:
    """Remove todas as tarefas (usado nos testes para isolar o estado)."""
    global _tarefas, _proximo_id
    _tarefas = []
    _proximo_id = 1
