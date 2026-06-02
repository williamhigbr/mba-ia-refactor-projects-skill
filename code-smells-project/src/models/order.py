class OrderModel:
    def __init__(self, db):
        self.db = db

    def create(self, usuario_id, total):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total)
        )
        self.db.commit()
        return cursor.lastrowid

    def add_item(self, pedido_id, produto_id, quantidade, preco_unitario):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, produto_id, quantidade, preco_unitario)
        )
        self.db.commit()

    def update_stock(self, produto_id, quantidade):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade, produto_id)
        )
        self.db.commit()

    def get_product(self, produto_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_by_user(self, usuario_id):
        return self._get_orders_with_items("WHERE p.usuario_id = ?", (usuario_id,))

    def get_all(self):
        return self._get_orders_with_items("", ())

    def update_status(self, pedido_id, novo_status):
        cursor = self.db.cursor()
        cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        self.db.commit()

    def get_sales_report(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(total), 0) as total FROM pedidos")
        row = cursor.fetchone()
        total_pedidos = row["cnt"]
        faturamento = row["total"]

        cursor.execute(
            "SELECT status, COUNT(*) as cnt FROM pedidos GROUP BY status"
        )
        status_counts = {r["status"]: r["cnt"] for r in cursor.fetchall()}

        return {
            "total_pedidos": total_pedidos,
            "faturamento": faturamento,
            "pendentes": status_counts.get("pendente", 0),
            "aprovados": status_counts.get("aprovado", 0),
            "cancelados": status_counts.get("cancelado", 0),
        }

    def _get_orders_with_items(self, where_clause, params):
        cursor = self.db.cursor()
        cursor.execute(f"""
            SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
                   i.produto_id, i.quantidade, i.preco_unitario,
                   pr.nome as produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido i ON i.pedido_id = p.id
            LEFT JOIN produtos pr ON pr.id = i.produto_id
            {where_clause}
            ORDER BY p.id
        """, params)
        rows = cursor.fetchall()

        orders = {}
        for row in rows:
            oid = row["id"]
            if oid not in orders:
                orders[oid] = {
                    "id": oid,
                    "usuario_id": row["usuario_id"],
                    "status": row["status"],
                    "total": row["total"],
                    "criado_em": row["criado_em"],
                    "itens": []
                }
            if row["produto_id"] is not None:
                orders[oid]["itens"].append({
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"]
                })
        return list(orders.values())
