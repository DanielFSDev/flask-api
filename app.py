from flask import Flask, request, jsonify
from flasgger import Swagger
app = Flask(__name__)
swagger = Swagger(app)
usuarios = []

@app.route('/usuarios', methods=['POST'])
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

    usuario = {
        'id': len(usuarios) + 1,
        'nome': dados['nome'],
        'email': dados['email']
    }
    usuarios.append(usuario)
    return jsonify(usuario), 201

@app.route('/usuarios', methods=['GET'])
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