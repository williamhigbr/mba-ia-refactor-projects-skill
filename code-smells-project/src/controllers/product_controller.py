VALID_CATEGORIES = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]


class ProductController:
    def __init__(self, product_model):
        self.model = product_model

    def list_all(self):
        produtos = self.model.get_all()
        return {"dados": produtos, "sucesso": True}, 200

    def get_by_id(self, product_id):
        produto = self.model.get_by_id(product_id)
        if produto:
            return {"dados": produto, "sucesso": True}, 200
        return {"erro": "Produto não encontrado", "sucesso": False}, 404

    def create(self, data):
        if not data:
            return {"erro": "Dados inválidos"}, 400
        nome = data.get("nome")
        preco = data.get("preco")
        estoque = data.get("estoque")
        if not nome:
            return {"erro": "Nome é obrigatório"}, 400
        if preco is None:
            return {"erro": "Preço é obrigatório"}, 400
        if estoque is None:
            return {"erro": "Estoque é obrigatório"}, 400
        descricao = data.get("descricao", "")
        categoria = data.get("categoria", "geral")
        if preco < 0:
            return {"erro": "Preço não pode ser negativo"}, 400
        if estoque < 0:
            return {"erro": "Estoque não pode ser negativo"}, 400
        if len(nome) < 2:
            return {"erro": "Nome muito curto"}, 400
        if len(nome) > 200:
            return {"erro": "Nome muito longo"}, 400
        if categoria not in VALID_CATEGORIES:
            return {"erro": f"Categoria inválida. Válidas: {VALID_CATEGORIES}"}, 400

        product_id = self.model.create(nome, descricao, preco, estoque, categoria)
        return {"dados": {"id": product_id}, "sucesso": True, "mensagem": "Produto criado"}, 201

    def update(self, product_id, data):
        if not self.model.get_by_id(product_id):
            return {"erro": "Produto não encontrado"}, 404
        if not data:
            return {"erro": "Dados inválidos"}, 400
        nome = data.get("nome")
        preco = data.get("preco")
        estoque = data.get("estoque")
        if not nome:
            return {"erro": "Nome é obrigatório"}, 400
        if preco is None:
            return {"erro": "Preço é obrigatório"}, 400
        if estoque is None:
            return {"erro": "Estoque é obrigatório"}, 400
        descricao = data.get("descricao", "")
        categoria = data.get("categoria", "geral")
        if preco < 0:
            return {"erro": "Preço não pode ser negativo"}, 400
        if estoque < 0:
            return {"erro": "Estoque não pode ser negativo"}, 400

        self.model.update(product_id, nome, descricao, preco, estoque, categoria)
        return {"sucesso": True, "mensagem": "Produto atualizado"}, 200

    def delete(self, product_id):
        if not self.model.get_by_id(product_id):
            return {"erro": "Produto não encontrado"}, 404
        self.model.delete(product_id)
        return {"sucesso": True, "mensagem": "Produto deletado"}, 200

    def search(self, termo, categoria, preco_min, preco_max):
        resultados = self.model.search(termo, categoria, preco_min, preco_max)
        return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200
