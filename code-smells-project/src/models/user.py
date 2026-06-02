class UserModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, user_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def create(self, nome, email, senha):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
            (nome, email, senha)
        )
        self.db.commit()
        return cursor.lastrowid

    def authenticate(self, email, senha):
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT id, nome, email, tipo FROM usuarios WHERE email = ? AND senha = ?",
            (email, senha)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
