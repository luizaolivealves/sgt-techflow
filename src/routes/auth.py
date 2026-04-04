"""
Rotas de Autenticação — SGT
Endpoints para registro e login de usuários.

POST /auth/registro  → cadastra novo usuário
POST /auth/login     → autentica e retorna token JWT
"""

from flask import Blueprint, request, jsonify
from src.models.usuario import Usuario, registrar_usuario, autenticar_usuario

# Blueprint de autenticação com prefixo /auth
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/registro", methods=["POST"])
def registro():
    """
    Cadastra um novo usuário no sistema.

    Corpo esperado (JSON):
        nome    (obrigatório): Nome completo.
        email   (obrigatório): E-mail único de acesso.
        senha   (obrigatório): Senha (mínimo 4 caracteres).
        perfil  (opcional):    ADMIN ou USUARIO (padrão: USUARIO).
    """
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Payload JSON obrigatório."}), 400

    try:
        usuario = Usuario(
            nome=dados.get("nome", ""),
            email=dados.get("email", ""),
            senha=dados.get("senha", ""),
            perfil=dados.get("perfil", "USUARIO"),
        )
        registrar_usuario(usuario)
        return jsonify({
            "mensagem": "Usuário registrado com sucesso.",
            "usuario": usuario.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Autentica um usuário e retorna uma confirmação de acesso.

    Corpo esperado (JSON):
        email (obrigatório): E-mail cadastrado.
        senha (obrigatório): Senha do usuário.

    Nota: Em produção, este endpoint retornaria um JWT. Aqui retornamos
    uma resposta simplificada para fins didáticos.
    """
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Payload JSON obrigatório."}), 400

    email = dados.get("email", "")
    senha = dados.get("senha", "")

    usuario = autenticar_usuario(email, senha)
    if not usuario:
        return jsonify({"erro": "Credenciais inválidas."}), 401

    # Em produção: retornar JWT com flask-jwt-extended
    return jsonify({
        "mensagem": "Login realizado com sucesso.",
        "usuario": usuario.to_dict(),
        "token": f"jwt-simulado-{usuario.email}"  # Simulação didática
    }), 200
