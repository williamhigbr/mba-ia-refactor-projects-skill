class EnrollmentModel {
  constructor(db) {
    this.db = db;
  }

  create(userId, courseId) {
    return new Promise((resolve, reject) => {
      this.db.run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [userId, courseId], function (err) {
        if (err) return reject(err);
        resolve(this.lastID);
      });
    });
  }

  findByCourseId(courseId) {
    return new Promise((resolve, reject) => {
      this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [courseId], (err, rows) => {
        if (err) return reject(err);
        resolve(rows);
      });
    });
  }
}

module.exports = EnrollmentModel;
