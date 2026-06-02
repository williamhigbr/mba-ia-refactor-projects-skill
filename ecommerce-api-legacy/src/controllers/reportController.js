const { PAYMENT_STATUS } = require('../config/constants');

class ReportController {
  constructor(courseModel, enrollmentModel, userModel, paymentModel) {
    this.courseModel = courseModel;
    this.enrollmentModel = enrollmentModel;
    this.userModel = userModel;
    this.paymentModel = paymentModel;
  }

  async getFinancialReport() {
    const courses = await this.courseModel.findAll();
    const report = [];

    for (const course of courses) {
      const courseData = { course: course.title, revenue: 0, students: [] };
      const enrollments = await this.enrollmentModel.findByCourseId(course.id);

      for (const enrollment of enrollments) {
        const user = await this.findUserById(enrollment.user_id);
        const payment = await this.paymentModel.findByEnrollmentId(enrollment.id);

        if (payment && payment.status === PAYMENT_STATUS.PAID) {
          courseData.revenue += payment.amount;
        }

        courseData.students.push({
          student: user ? user.name : 'Unknown',
          paid: payment ? payment.amount : 0,
        });
      }

      report.push(courseData);
    }

    return { status: 200, body: report };
  }

  findUserById(id) {
    return new Promise((resolve, reject) => {
      this.userModel.db.get("SELECT name, email FROM users WHERE id = ?", [id], (err, row) => {
        if (err) return reject(err);
        resolve(row || null);
      });
    });
  }
}

module.exports = ReportController;
