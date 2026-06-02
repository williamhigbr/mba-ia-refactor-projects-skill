from flask import Blueprint, request, jsonify

user_bp = Blueprint("users", __name__)
_controller = None


def init_user_routes(controller):
    global _controller
    _controller = controller


@user_bp.route("/usuarios", methods=["GET"])
def list_users():
    payload, status = _controller.list_all()
    return jsonify(payload), status


@user_bp.route("/usuarios/<int:id>", methods=["GET"])
def get_user(id):
    payload, status = _controller.get_by_id(id)
    return jsonify(payload), status


@user_bp.route("/usuarios", methods=["POST"])
def create_user():
    payload, status = _controller.create(request.get_json() or {})
    return jsonify(payload), status


@user_bp.route("/login", methods=["POST"])
def login():
    payload, status = _controller.login(request.get_json() or {})
    return jsonify(payload), status
