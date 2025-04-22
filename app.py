from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import re
import os
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = os.getenv('JWT_ACCESS_TOKEN_EXPIRES')
app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM')

jwt = JWTManager(app)
swagger = Swagger(app)
usuarios = []


credenciais = {'admin': 'senha123'}
@app.route('/login', methods=['POST'])
def login():
    """
    Realizar login e obter token JWT
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            usuario:
              type: string
            senha:
              type: string
    responses:
      200:
        description: Token JWT gerado com sucesso
      401:
        description: Credenciais inválidas
    """
    dados = request.get_json()
    usuario = dados.get('usuario')
    senha = dados.get('senha')

    if credenciais.get(usuario) == senha:
        token = create_access_token(identity=usuario)
        return jsonify({'token': token}), 200

    return jsonify({'erro': 'Credenciais inválidas'}), 401

@app.route('/usuarios', methods=['POST'])
@jwt_required()
def cadastrar_usuario():
    """
    Cadastrar um novo usuário
    ---
    tags:
      - Usuários
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
            email:
              type: string
    responses:
      201:
        description: Usuário cadastrado com sucesso
      400:
        description: Dados inválidos
    """
    dados = request.get_json()
    erro = validar_dados(dados, {'nome': str, 'email': str})
    if erro:
        return resposta_erro(erro, 400)

    if not re.match(r"[^@]+@[^@]+\.[^@]+", dados['email']):
        return resposta_erro("Formato de email inválido", 400)

    if any(u['email'] == dados['email'] for u in usuarios):
        return resposta_erro("Email já cadastrado", 400)

    usuario = {
        'id': len(usuarios) + 1,
        'nome': dados['nome'],
        'email': dados['email']
    }
    usuarios.append(usuario)
    return jsonify(usuario), 201

@app.route('/usuarios', methods=['GET'])
@jwt_required()
def listar_usuarios():
    """
    Listar todos os usuários
    ---
    tags:
      - Usuários
    responses:
      200:
        description: Lista de usuários
    """
    return jsonify(usuarios), 200

@app.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
@jwt_required()
def deletar_usuario(usuario_id):
    """
    Deletar um usuário pelo ID
    ---
    tags:
      - Usuários
    parameters:
      - in: path
        name: usuario_id
        required: true
        type: integer
    responses:
      200:
        description: Usuário deletado com sucesso
      404:
        description: Usuário não encontrado
    """
    global usuarios
    usuario = next((u for u in usuarios if u['id'] == usuario_id), None)
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    usuarios = [u for u in usuarios if u['id'] != usuario_id]
    return jsonify({'mensagem': 'Usuário deletado com sucesso'}), 200

@app.route('/usuarios/<int:usuario_id>', methods=['PUT'])
@jwt_required()
def alterar_usuario(usuario_id):
    """
    Alterar os dados de um usuário pelo ID
    ---
    tags:
      - Usuários
    parameters:
      - in: path
        name: usuario_id
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
            email:
              type: string
    responses:
      200:
        description: Usuário alterado com sucesso
      400:
        description: Dados inválidos
      404:
        description: Usuário não encontrado
    """
    dados = request.get_json()
    erro = validar_dados(dados, {'nome': str, 'email': str})
    if erro:
        return resposta_erro(erro, 400)

    usuario = next((u for u in usuarios if u['id'] == usuario_id), None)
    if not usuario:
        return resposta_erro('Usuário não encontrado.', 404)

    usuario['nome'] = dados['nome']
    usuario['email'] = dados['email']
    return jsonify(usuario), 200

def resposta_erro(mensagem, codigo):
    """Função para padronizar respostas de erro."""
    return jsonify({'erro': mensagem}), codigo

def validar_dados(dados, campos_obrigatorios):
    """Valida se os campos obrigatórios estão presentes e são válidos."""
    for campo, tipo in campos_obrigatorios.items():
        if campo not in dados:
            return f"Campo '{campo}' é obrigatório."
        if not isinstance(dados[campo], tipo):
            return f"Campo '{campo}' deve ser do tipo {tipo.__name__}."
    return None

if __name__ == '__main__':
    app.run(debug=True)