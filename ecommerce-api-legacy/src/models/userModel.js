class UserModel {
  constructor(db) {
    this.db = db;
  }

  findByEmail(email) {
    return new Promise((resolve, reject) => {
      this.db.get("SELECT id, name, email FROM users WHERE email = ?", [email], (err, row) => {
        if (err) return reject(err);
        resolve(row || null);
      });
    });
  }

  create(name, email, hashedPassword) {
    return new Promise((resolve, reject) => {
      this.db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [name, email, hashedPassword], function (err) {
        if (err) return reject(err);
        resolve(this.lastID);
      });
    });
  }

  deleteById(id) {
    return new Promise((resolve, reject) => {
      this.db.run("DELETE FROM users WHERE id = ?", [id], function (err) {
        if (err) return reject(err);
        resolve(this.changes);
      });
    });
  }
}

module.exports = UserModel;
