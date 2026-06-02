from flask import Flask, jsonify
from flask_cors import CORS

from src.config import Config
from src.config.database import create_db
from src.models.product import ProductModel
from src.models.user import UserModel
from src.models.order import OrderModel
from src.controllers.product_controller import ProductController
from src.controllers.user_controller import UserController
from src.controllers.order_controller import OrderController
from src.routes.product_routes import product_bp, init_product_routes
from src.routes.user_routes import user_bp, init_user_routes
from src.routes.order_routes import order_bp, init_order_routes
from src.routes.admin_routes import admin_bp, init_admin_routes
from src.middlewares.error_handler import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["DEBUG"] = Config.DEBUG
    CORS(app)

    # Infrastructure
    db = create_db(Config.DB_PATH)

    # Models
    product_model = ProductModel(db)
    user_model = UserModel(db)
    order_model = OrderModel(db)

    # Controllers
    product_controller = ProductController(product_model)
    user_controller = UserController(user_model)
    order_controller = OrderController(order_model)

    # Routes
    init_product_routes(product_controller)
    init_user_routes(user_controller)
    init_order_routes(order_controller)
    init_admin_routes(db, Config)

    # Register blueprints
    app.register_blueprint(product_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)

    # Error handlers
    register_error_handlers(app)

    # Health and index
    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health"
            }
        })

    @app.route("/health", methods=["GET"])
    def health_check():
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0]
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": produtos,
                "usuarios": usuarios,
                "pedidos": pedidos
            },
            "versao": "1.0.0"
        })

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host=Config.HOST, port=Config.PORT)
