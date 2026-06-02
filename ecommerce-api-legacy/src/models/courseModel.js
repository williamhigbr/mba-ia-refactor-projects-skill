class CourseModel {
  constructor(db) {
    this.db = db;
  }

  findActiveById(id) {
    return new Promise((resolve, reject) => {
      this.db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [id], (err, row) => {
        if (err) return reject(err);
        resolve(row || null);
      });
    });
  }

  findAll() {
    return new Promise((resolve, reject) => {
      this.db.all("SELECT * FROM courses", [], (err, rows) => {
        if (err) return reject(err);
        resolve(rows);
      });
    });
  }
}

module.exports = CourseModel;
