from flask import Blueprint, jsonify

admin_bp = Blueprint("admin", __name__)
_db = None
_config = None


def init_admin_routes(db, config):
    global _db, _config
    _db = db
    _config = config


@admin_bp.route("/admin/reset-db", methods=["POST"])
def reset_database():
    if not _config.ALLOW_DB_RESET:
        return jsonify({"erro": "Operação desabilitada neste ambiente"}), 403
    cursor = _db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    _db.commit()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
