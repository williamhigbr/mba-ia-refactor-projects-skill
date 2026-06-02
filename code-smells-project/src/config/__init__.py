import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-development")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    ALLOW_DB_RESET = os.environ.get("ALLOW_DB_RESET", "false").lower() == "true"
