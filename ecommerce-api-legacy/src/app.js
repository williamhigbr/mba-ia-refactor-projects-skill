const express = require('express');
const { config } = require('./config/settings');
const { createDatabase } = require('./models/database');
const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const CheckoutController = require('./controllers/checkoutController');
const ReportController = require('./controllers/reportController');
const UserController = require('./controllers/userController');
const { createRoutes } = require('./routes/index');
const { errorHandler } = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

// Composition root — wire dependencies
const db = createDatabase();
const userModel = new UserModel(db);
const courseModel = new CourseModel(db);
const enrollmentModel = new EnrollmentModel(db);
const paymentModel = new PaymentModel(db);
const auditLogModel = new AuditLogModel(db);

const checkoutController = new CheckoutController(userModel, courseModel, enrollmentModel, paymentModel, auditLogModel);
const reportController = new ReportController(courseModel, enrollmentModel, userModel, paymentModel);
const userController = new UserController(userModel);

app.use(createRoutes(checkoutController, reportController, userController));
app.use(errorHandler);

const port = config.port;
app.listen(port, () => {
  console.log(`LMS API running on port ${port}`);
});

module.exports = app;
