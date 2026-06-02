class AuditLogModel {
  constructor(db) {
    this.db = db;
  }

  create(action) {
    return new Promise((resolve, reject) => {
      this.db.run("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [action], function (err) {
        if (err) return reject(err);
        resolve(this.lastID);
      });
    });
  }
}

module.exports = AuditLogModel;
