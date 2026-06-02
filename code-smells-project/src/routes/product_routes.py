from flask import Blueprint, request, jsonify

product_bp = Blueprint("products", __name__)
_controller = None


def init_product_routes(controller):
    global _controller
    _controller = controller


@product_bp.route("/produtos", methods=["GET"])
def list_products():
    payload, status = _controller.list_all()
    return jsonify(payload), status


@product_bp.route("/produtos/busca", methods=["GET"])
def search_products():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None, type=float)
    preco_max = request.args.get("preco_max", None, type=float)
    payload, status = _controller.search(termo, categoria, preco_min, preco_max)
    return jsonify(payload), status


@product_bp.route("/produtos/<int:id>", methods=["GET"])
def get_product(id):
    payload, status = _controller.get_by_id(id)
    return jsonify(payload), status


@product_bp.route("/produtos", methods=["POST"])
def create_product():
    payload, status = _controller.create(request.get_json() or {})
    return jsonify(payload), status


@product_bp.route("/produtos/<int:id>", methods=["PUT"])
def update_product(id):
    payload, status = _controller.update(id, request.get_json() or {})
    return jsonify(payload), status


@product_bp.route("/produtos/<int:id>", methods=["DELETE"])
def delete_product(id):
    payload, status = _controller.delete(id)
    return jsonify(payload), status
