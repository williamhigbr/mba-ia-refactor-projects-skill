class UserController:
    def __init__(self, user_model):
        self.model = user_model

    def list_all(self):
        usuarios = self.model.get_all()
        return {"dados": usuarios, "sucesso": True}, 200

    def get_by_id(self, user_id):
        usuario = self.model.get_by_id(user_id)
        if usuario:
            return {"dados": usuario, "sucesso": True}, 200
        return {"erro": "Usuário não encontrado"}, 404

    def create(self, data):
        if not data:
            return {"erro": "Dados inválidos"}, 400
        nome = data.get("nome", "")
        email = data.get("email", "")
        senha = data.get("senha", "")
        if not nome or not email or not senha:
            return {"erro": "Nome, email e senha são obrigatórios"}, 400
        user_id = self.model.create(nome, email, senha)
        return {"dados": {"id": user_id}, "sucesso": True}, 201

    def login(self, data):
        if not data:
            return {"erro": "Dados inválidos"}, 400
        email = data.get("email", "")
        senha = data.get("senha", "")
        if not email or not senha:
            return {"erro": "Email e senha são obrigatórios"}, 400
        usuario = self.model.authenticate(email, senha)
        if usuario:
            return {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}, 200
        return {"erro": "Email ou senha inválidos", "sucesso": False}, 401
