from flask import Blueprint, request, jsonify

order_bp = Blueprint("orders", __name__)
_controller = None


def init_order_routes(controller):
    global _controller
    _controller = controller


@order_bp.route("/pedidos", methods=["POST"])
def create_order():
    payload, status = _controller.create(request.get_json() or {})
    return jsonify(payload), status


@order_bp.route("/pedidos", methods=["GET"])
def list_orders():
    payload, status = _controller.list_all()
    return jsonify(payload), status


@order_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def list_user_orders(usuario_id):
    payload, status = _controller.list_by_user(usuario_id)
    return jsonify(payload), status


@order_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def update_order_status(pedido_id):
    payload, status = _controller.update_status(pedido_id, request.get_json() or {})
    return jsonify(payload), status


@order_bp.route("/relatorios/vendas", methods=["GET"])
def sales_report():
    payload, status = _controller.sales_report()
    return jsonify(payload), status
