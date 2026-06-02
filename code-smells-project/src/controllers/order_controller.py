DISCOUNT_TIER_1_THRESHOLD = 10000
DISCOUNT_TIER_1_RATE = 0.1
DISCOUNT_TIER_2_THRESHOLD = 5000
DISCOUNT_TIER_2_RATE = 0.05
DISCOUNT_TIER_3_THRESHOLD = 1000
DISCOUNT_TIER_3_RATE = 0.02

VALID_STATUSES = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


class OrderController:
    def __init__(self, order_model):
        self.model = order_model

    def create(self, data):
        if not data:
            return {"erro": "Dados inválidos"}, 400
        usuario_id = data.get("usuario_id")
        itens = data.get("itens", [])
        if not usuario_id:
            return {"erro": "Usuario ID é obrigatório"}, 400
        if not itens:
            return {"erro": "Pedido deve ter pelo menos 1 item"}, 400

        # Validate stock and calculate total
        total = 0
        validated_items = []
        for item in itens:
            produto = self.model.get_product(item["produto_id"])
            if produto is None:
                return {"erro": f"Produto {item['produto_id']} não encontrado"}, 400
            if produto["estoque"] < item["quantidade"]:
                return {"erro": f"Estoque insuficiente para {produto['nome']}"}, 400
            total += produto["preco"] * item["quantidade"]
            validated_items.append((item["produto_id"], item["quantidade"], produto["preco"]))

        # Create order and items
        pedido_id = self.model.create(usuario_id, total)
        for produto_id, quantidade, preco in validated_items:
            self.model.add_item(pedido_id, produto_id, quantidade, preco)
            self.model.update_stock(produto_id, quantidade)

        return {"dados": {"pedido_id": pedido_id, "total": total}, "sucesso": True, "mensagem": "Pedido criado com sucesso"}, 201

    def list_by_user(self, usuario_id):
        pedidos = self.model.get_by_user(usuario_id)
        return {"dados": pedidos, "sucesso": True}, 200

    def list_all(self):
        pedidos = self.model.get_all()
        return {"dados": pedidos, "sucesso": True}, 200

    def update_status(self, pedido_id, data):
        if not data:
            return {"erro": "Dados inválidos"}, 400
        novo_status = data.get("status", "")
        if novo_status not in VALID_STATUSES:
            return {"erro": "Status inválido"}, 400
        self.model.update_status(pedido_id, novo_status)
        return {"sucesso": True, "mensagem": "Status atualizado"}, 200

    def sales_report(self):
        report = self.model.get_sales_report()
        faturamento = report["faturamento"]

        desconto = 0
        if faturamento > DISCOUNT_TIER_1_THRESHOLD:
            desconto = faturamento * DISCOUNT_TIER_1_RATE
        elif faturamento > DISCOUNT_TIER_2_THRESHOLD:
            desconto = faturamento * DISCOUNT_TIER_2_RATE
        elif faturamento > DISCOUNT_TIER_3_THRESHOLD:
            desconto = faturamento * DISCOUNT_TIER_3_RATE

        return {"dados": {
            "total_pedidos": report["total_pedidos"],
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": report["pendentes"],
            "pedidos_aprovados": report["aprovados"],
            "pedidos_cancelados": report["cancelados"],
            "ticket_medio": round(faturamento / report["total_pedidos"], 2) if report["total_pedidos"] > 0 else 0
        }, "sucesso": True}, 200
