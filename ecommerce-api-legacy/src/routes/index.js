const { Router } = require('express');

function createRoutes(checkoutController, reportController, userController) {
  const router = Router();

  router.post('/api/checkout', async (req, res, next) => {
    try {
      const data = {
        userName: req.body.usr,
        email: req.body.eml,
        password: req.body.pwd,
        courseId: req.body.c_id,
        cardNumber: req.body.card,
      };
      const result = await checkoutController.execute(data);
      res.status(result.status).json(result.body);
    } catch (err) {
      next(err);
    }
  });

  router.get('/api/admin/financial-report', async (req, res, next) => {
    try {
      const result = await reportController.getFinancialReport();
      res.status(result.status).json(result.body);
    } catch (err) {
      next(err);
    }
  });

  router.delete('/api/users/:id', async (req, res, next) => {
    try {
      const result = await userController.deleteUser(req.params.id);
      res.status(result.status).json(result.body);
    } catch (err) {
      next(err);
    }
  });

  return router;
}

module.exports = { createRoutes };
