const crypto = require('crypto');
const { PAYMENT_STATUS } = require('../config/constants');

class CheckoutController {
  constructor(userModel, courseModel, enrollmentModel, paymentModel, auditLogModel) {
    this.userModel = userModel;
    this.courseModel = courseModel;
    this.enrollmentModel = enrollmentModel;
    this.paymentModel = paymentModel;
    this.auditLogModel = auditLogModel;
  }

  async execute(data) {
    const { userName, email, password, courseId, cardNumber } = data;

    if (!userName || !email || !courseId || !cardNumber) {
      return { status: 400, body: { error: 'Bad Request' } };
    }

    const course = await this.courseModel.findActiveById(courseId);
    if (!course) {
      return { status: 404, body: { error: 'Curso não encontrado' } };
    }

    let user = await this.userModel.findByEmail(email);
    let userId;

    if (!user) {
      const hashedPassword = this.hashPassword(password || '123456');
      userId = await this.userModel.create(userName, email, hashedPassword);
    } else {
      userId = user.id;
    }

    const paymentStatus = this.processPayment(cardNumber);
    if (paymentStatus === PAYMENT_STATUS.DENIED) {
      return { status: 400, body: { error: 'Pagamento recusado' } };
    }

    const enrollmentId = await this.enrollmentModel.create(userId, courseId);
    await this.paymentModel.create(enrollmentId, course.price, paymentStatus);
    await this.auditLogModel.create(`Checkout curso ${courseId} por ${userId}`);

    return { status: 200, body: { msg: 'Sucesso', enrollment_id: enrollmentId } };
  }

  hashPassword(password) {
    return crypto.createHash('sha256').update(password).digest('hex');
  }

  processPayment(cardNumber) {
    return cardNumber.startsWith('4') ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
  }
}

module.exports = CheckoutController;
