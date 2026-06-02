class PaymentModel {
  constructor(db) {
    this.db = db;
  }

  create(enrollmentId, amount, status) {
    return new Promise((resolve, reject) => {
      this.db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [enrollmentId, amount, status], function (err) {
        if (err) return reject(err);
        resolve(this.lastID);
      });
    });
  }

  findByEnrollmentId(enrollmentId) {
    return new Promise((resolve, reject) => {
      this.db.get("SELECT amount, status FROM payments WHERE enrollment_id = ?", [enrollmentId], (err, row) => {
        if (err) return reject(err);
        resolve(row || null);
      });
    });
  }
}

module.exports = PaymentModel;
